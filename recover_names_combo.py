import os
import re
import sqlite3
import shutil
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
                    base = os.path.splitext(f)[0]
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
    stop_words = {'컨설팅','컨설턴트','경력','신입','기획','개발','채용','마케팅','디자인','운영','영업','전략','재무','회계','인사','총무','데이터','분석','사업','관리','팀장','리더','매니저','매니져','지원','담당','담당자','자산','운용', '팀', '파트', '설계', '보안', '경영', '정보', '솔루션'}
    valid_matches = [m for m in matches if m not in stop_words and len(m) >= 2]
    return valid_matches[0] if valid_matches else None

def main():
    print("0. DB 복원 (오류 나기 직전 백업본 candidates_backup_namefix.db에서 롤백)")
    shutil.copy('candidates_backup_namefix.db', 'candidates.db')
    
    conn = sqlite3.connect('candidates.db')
    cur = conn.cursor()
    
    cur.execute("SELECT id, document_hash, raw_text FROM candidates")
    db_rows = cur.fetchall()
    
    # 1. document_hash -> id 매핑
    db_hashes_map = {row[1]: row[0] for row in db_rows if row[1]}
    
    files = collect_files()
    print(f"\n1. 발견된 로컬 파일 수: {len(files)}")
    
    updates = []
    prefix_map = {}
    
    # 2. 파일 스캔: Hash 기반 1차 매칭 & Prefix 맵 구축
    for fname, filepath in tqdm(files.items(), desc="Extracting Texts & Hashing"):
        base = os.path.splitext(fname)[0]
        name = get_korean_name(base)
        if not name:
            continue
            
        text = extract_text(filepath)
        if not text:
            continue
            
        # Hash 기반 1차 매칭 (엄격하고 정확함)
        doc_hash = hashlib.sha256(text.encode('utf-8')).hexdigest()
        if doc_hash in db_hashes_map:
            _id = db_hashes_map[doc_hash]
            updates.append((name, _id))
            # 이미 찾았으므로 db_hashes_map에서 제거하여 중복 방지
            del db_hashes_map[doc_hash]
        else:
            # Hash 불일치 시 Prefix 기반 Fallback을 위해 맵 저장
            stripped = re.sub(r'\s+', '', text[:2000])
            prefix = stripped[:80]
            if prefix and len(prefix) >= 20: # 빈 키 방지
                prefix_map[prefix] = name

    print(f"\n3. Hash 기반 1차 매칭 완료: {len(updates)}건")
    
    # Prefix 맵 구조 확인
    print("\n   Prefix 맵 크기:", len(prefix_map))
    if prefix_map:
        print("   Prefix 맵 첫 항목:", list(prefix_map.keys())[0][:20], "->", list(prefix_map.values())[0])

    # 3. Hash 불일치 대상에 대해 Prefix 기반 2차 매칭
    unmatched_rows = [row for row in db_rows if row[1] in db_hashes_map]
    print(f"\n4. Hash 불일치 대상 {len(unmatched_rows)}건에 대한 Prefix 2차 매칭 진행...")
    
    prefix_matched = 0
    for row in unmatched_rows:
        _id = row[0]
        raw_text = row[2]
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
            prefix_matched += 1
            
    print(f"   Prefix 2차 매칭 성공: {prefix_matched}건")
    print(f"\n5. 총 업데이트 대상: {len(updates)}건 (전체 2886건 중)")
    
    # 중복 제거
    unique_updates = []
    seen_ids = set()
    for u in updates:
        if u[1] not in seen_ids:
            unique_updates.append(u)
            seen_ids.add(u[1])
            
    cur.executemany("UPDATE candidates SET name_kr = ? WHERE id = ?", unique_updates)
    conn.commit()
    
    print("\n6. 완료 후 상위 이름 분포 (Top 10):")
    cur.execute("SELECT name_kr, count(*) FROM candidates GROUP BY name_kr ORDER BY count(*) DESC LIMIT 10")
    results = cur.fetchall()
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
