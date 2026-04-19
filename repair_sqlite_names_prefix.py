import os
import re
import sqlite3
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
    
    stop_words = "('자금', '기획', '개발', '운영', '마케팅', '재무', '회계', '전략', '인사', '총무', '법무', '구매기획팀', '경영정보팀', '개인정보보호', '보안컨설팅', '보안 솔루션 총판영업', '연구개발 차량설계', 'UX컨설팅', 'UIUX Designer', 'Main controller HW', 'IT DT', '물류 운영,개발')"
    cur.execute(f"SELECT id, raw_text, name_kr FROM candidates WHERE name_kr IN {stop_words} OR length(name_kr) > 10 OR name_kr LIKE '%부문%' OR name_kr LIKE '%팀%'")
    rows = cur.fetchall()
    
    print(f"Found {len(rows)} corrupted candidates in DB to fix.")
    
    files = collect_files()
    print(f"Discovered {len(files)} local physical files.")
    
    # Prefix map mapping text prefix -> base_name
    prefix_map = {}
    for base_name, filepath in tqdm(files.items(), desc="Extracting text snippets"):
        text = extract_text(filepath)
        if text:
            # use 500 chars, stripped of whitespace
            stripped_text = re.sub(r'\s+', '', text[:1500])
            prefix_map[stripped_text[:100]] = base_name

    updated_count = 0
    not_found = 0
    for row in rows:
        _id = row[0]
        raw_text = row[1]
        
        stripped_db_text = re.sub(r'\s+', '', raw_text[:1500])
        db_prefix = stripped_db_text[:100]
        
        base_name = None
        for file_prefix, fname in prefix_map.items():
            if file_prefix == db_prefix or file_prefix in db_prefix or db_prefix in file_prefix:
                base_name = fname
                break
                
        if base_name:
            new_name = get_korean_name(base_name)
            if new_name:
                cur.execute("UPDATE candidates SET name_kr = ? WHERE id = ?", (new_name, _id))
                updated_count += cur.rowcount
            else:
                # If get_korean_name failed but it's english, just use clean base_name
                clean = re.sub(r'\[.*?\]|\(.*?\)|\..*', '', base_name).strip()
                cur.execute("UPDATE candidates SET name_kr = ? WHERE id = ?", (clean, _id))
                updated_count += cur.rowcount
        else:
            # Fallback: if name_kr is just long but has real name, parse it
            parsed = get_korean_name(row[2])
            if parsed and parsed != row[2]:
                cur.execute("UPDATE candidates SET name_kr = ? WHERE id = ?", (parsed, _id))
                updated_count += cur.rowcount
            else:
                not_found += 1
                
    conn.commit()
    print(f"Updated {updated_count} names in SQLite. Failed to map {not_found} files.")

if __name__ == "__main__":
    main()
