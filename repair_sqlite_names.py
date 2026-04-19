import os
import re
import sqlite3
import hashlib
from tqdm import tqdm
from docx import Document
import fitz

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

def main():
    conn = sqlite3.connect('candidates.db')
    cur = conn.cursor()
    
    # 1. We don't want to re-extract all PDFs if we don't need to.
    # What if we just use the current raw_text in SQLite?
    # Actually, SQLite has raw_text in the DB!
    # BUT wait, the base_name is NOT in SQLite. We need base_name from the file!
    # If we hash the SQLite raw_text, we still don't have the file name. 
    # BUT wait, what if we just loop over SQLite. If name_kr is corrupted, we don't know the file name.
    # We HAVE to map from the file system.
    # To speed it up, we can hash the files and update SQLite.
    
    files = collect_files()
    print(f"Discovered {len(files)} resumes. Building hash map from DB...")
    
    # Fetch existing DB hashes to avoid unnecessary extraction
    cur.execute("SELECT id, document_hash FROM candidates")
    db_hashes = {row[1]: row[0] for row in cur.fetchall()}
    
    print(f"Loaded {len(db_hashes)} hashes from candidates.db")
    
    updated_count = 0
    # Process files
    for base_name, filepath in tqdm(files.items(), desc="Patching names"):
        name_kr = get_korean_name(base_name)
        if not name_kr: continue
        
        # We need the hash of the file to link it to SQLite.
        text = extract_text(filepath)
        doc_hash = hashlib.sha256(text.encode('utf-8')).hexdigest()
        
        if doc_hash in db_hashes:
            _id = db_hashes[doc_hash]
            cur.execute("UPDATE candidates SET name_kr = ? WHERE id = ?", (name_kr, _id))
            updated_count += cur.rowcount
            
    conn.commit()
    print(f"Updated {updated_count} names in SQLite based on physical files.")
    
if __name__ == "__main__":
    main()
