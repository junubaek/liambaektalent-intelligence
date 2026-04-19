import os
import re
from neo4j import GraphDatabase
import sqlite3
from tqdm import tqdm
import fitz
from docx import Document

FOLDER1 = r"C:\Users\cazam\Downloads\02_resume 전처리"
FOLDER2 = r"C:\Users\cazam\Downloads\02_resume_converted_docx"
FOLDER3 = r"C:\Users\cazam\Downloads\02_resume_converted_v8"

def collect_files():
    files = {}
    for folder in [FOLDER1, FOLDER2, FOLDER3]:
        if os.path.exists(folder):
            for f in os.listdir(folder):
                if f.endswith((".pdf", ".docx", ".doc")):
                    base_name = f.rsplit(".", 1)[0]
                    if base_name not in files:
                        files[base_name] = os.path.join(folder, f)
    return files

def extract_text(filepath):
    ext = filepath.rsplit(".", 1)[-1].lower()
    try:
        if ext == "pdf":
            doc = fitz.open(filepath)
            return "\n".join(page.get_text() for page in doc)
        elif ext in ("docx", "doc"):
            doc = Document(filepath)
            return "\n".join(p.text for p in doc.paragraphs)
    except:
        pass
    return ""

def get_korean_name(raw_name):
    clean = re.sub(r'\[.*?\]', '', raw_name)
    clean = re.sub(r'\(.*?\)', '', clean)
    clean = re.sub(r'부문|원본|최종|포트폴리오|이력서|합격|이력|Resume|CV', '', clean, flags=re.IGNORECASE)
    matches = re.findall(r'[가-힣]{2,4}', clean)
    
    stop_words = {'컨설팅','컨설턴트','경력','신입','기획','개발','채용','마케팅','디자인','운영','영업','전략','재무','회계','인사','총무','개발자','엔지니어','데이터','분석','사업','관리','팀장','리더','매니저','매니져','지원','담당','담당자','자산','운용', '팀', '파트', '설계', '보안', '부문', '부문장', '기획팀', '개발팀', '운영팀', '경영', '정보', '솔루션'}
    valid_matches = [m for m in matches if m not in stop_words]
    
    name_kr = valid_matches[-1] if valid_matches else (matches[-1] if matches else clean.strip())
    
    for suffix in ['부문', '팀', '파트']:
        if name_kr.endswith(suffix) and len(name_kr) > len(suffix):
            name_kr = name_kr[:-len(suffix)]
            
    return name_kr

def extract_phone(text):
    match = re.search(r'010[- .]?\d{4}[- .]?\d{4}', text)
    return match.group(0) if match else ""

def extract_email(text):
    match = re.search(r'[\w.-]+@[\w.-]+\.\w+', text)
    return match.group(0) if match else ""

def main():
    driver = GraphDatabase.driver('neo4j://127.0.0.1:7687', auth=('neo4j', 'toss1234'))
    conn = sqlite3.connect('candidates.db')
    cur = conn.cursor()
    
    files = collect_files()
    print(f"Discovered {len(files)} resumes for background extraction.")
    
    updated_count = 0
    phone_extracted_count = 0
    email_extracted_count = 0
    
    with driver.session() as session:
        # 1. Instantly patch ALL name_kr first without requiring heavy file I/O
        print("Phase 1: Instantly patching name_kr across all graph nodes...")
        result = session.run("MATCH (c:Candidate) RETURN c.id AS id, c.name AS name")
        records = [{"id": r["id"], "name": r["name"]} for r in result]
        for r in tqdm(records, desc="Patching name_kr"):
            node_id = r["id"]
            node_name = r["name"]
            name_kr = get_korean_name(node_name)
            if name_kr:
                session.run("MATCH (c:Candidate {id: $id}) SET c.name_kr = $name_kr", id=node_id, name_kr=name_kr)
                cur.execute("UPDATE candidates SET name_kr = ? WHERE id = ?", (name_kr, node_id))
        conn.commit()
        
        # # 2. Heavier Text Extraction Routine
        # print("Phase 2: Extracting Contact Metadata from physical files...")
        # for name, filepath in tqdm(files.items(), desc="Extracting phones/emails"):
        #     text = extract_text(filepath)
        #     phone = extract_phone(text)
        #     email = extract_email(text)
        #     
        #     if phone or email:
        #         if phone: phone_extracted_count += 1
        #         if email: email_extracted_count += 1
        #         
        #         query_parts = []
        #         if phone: query_parts.append("c.phone = $phone")
        #         if email: query_parts.append("c.email = $email")
        #         
        #         query = f"MATCH (c:Candidate {{name: $name}}) SET {', '.join(query_parts)} RETURN c"
        #         res = session.run(query, name=name, phone=phone, email=email)
        #         if res.single():
        #             updated_count += 1
        
    print(f"✅ Metadata Extraction Operation Completed.")
    print(f"Phase 1 Neo4j + SQLite name patching finished.")

if __name__ == "__main__":
    main()
