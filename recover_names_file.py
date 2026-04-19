import os
import re
import sqlite3
import shutil
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
                    files[f] = os.path.join(folder, f)
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
    
    stop_words = {'컨설팅','컨설턴트','경력','신입','기획','개발','채용','마케팅','디자인','운영','영업','전략','재무','회계','인사','총무','개발자','엔지니어','데이터','분석','사업','관리','팀장','리더','매니저','매니져','지원','담당','담당자','자산','운용', '팀', '파트', '설계', '보안', '경영', '정보', '솔루션'}
    valid_matches = [m for m in matches if m not in stop_words and len(m) >= 2]
    
    name_kr = valid_matches[0] if valid_matches else None
    return name_kr

def main():
    print("0. DB 복원...")
    # Rollback from backup to get the "김대용" state back from the failed regex state
    shutil.copy('candidates_backup_namefix.db', 'candidates.db')
    
    files = collect_files()
    print(f"\n1. 파일 수: {len(files)}")
    print("샘플:", list(files.keys())[:5])
    
    prefix_map = {}
    print("\n2. 안전한 파일명 -> 이름 매핑 중...")
    
    for fname, filepath in tqdm(files.items(), desc="Extracting Texts"):
        base = os.path.splitext(fname)[0]
        
        name = get_korean_name(base)
        if not name:
            continue
            
        text = extract_text(filepath)
        if not text:
            continue
            
        stripped = re.sub(r'\s+', '', text[:2000])
        prefix = stripped[:80]
        
        # 핵심 버그 방지: 빈 키 절대 금지 & 너무 짧은 접두사 무시 (공통 양식 방지)
        if not prefix or len(prefix) < 20:
            continue
            
        prefix_map[prefix] = name

    print("\n4. 매핑 샘플 10건:")
    for k, v in list(prefix_map.items())[:10]:
        print(f"  [{k[:30]}...] -> {v}")
        
    conn = sqlite3.connect('candidates.db')
    cursor = conn.cursor()
    
    cursor.execute("SELECT id, raw_text FROM candidates")
    rows = cursor.fetchall()
    
    updates = []
    print("\n5. DB 업데이트 매칭 중...")
    for row in rows:
        _id = row[0]
        raw_text = row[1]
        
        if not raw_text:
            continue
            
        stripped_db = re.sub(r'\s+', '', raw_text[:2000])
        db_prefix = stripped_db[:80]
        
        if not db_prefix or len(db_prefix) < 20:
            continue
            
        matched_name = None
        for p_key, p_name in prefix_map.items():
            if p_key in db_prefix or db_prefix in p_key:
                matched_name = p_name
                break
                
        if matched_name:
            updates.append((matched_name, _id))
            
    print(f"매핑된 업데이트 대상: {len(updates)}건")
    cursor.executemany("UPDATE candidates SET name_kr = ? WHERE id = ?", updates)
    conn.commit()
    
    print("\n6. 완료 후 상위 이름 분포 (Top 10):")
    cursor.execute("SELECT name_kr, count(*) FROM candidates GROUP BY name_kr ORDER BY count(*) DESC LIMIT 10")
    results = cursor.fetchall()
    for row in results:
        print(f"  '{row[0]}': {row[1]}명")
        
    if results and results[0][1] >= 100:
        print("\n🚨 [위험] 아직도 동일 이름이 100명 이상입니다! 자동 롤백을 진행합니다.")
        conn.close()
        shutil.copy('candidates_backup_namefix.db', 'candidates.db')
        print("롤백 완료.")
    else:
        print("\n✅ 분포가 안정적입니다. 성공적으로 복구되었습니다.")
        conn.close()

if __name__ == "__main__":
    main()
