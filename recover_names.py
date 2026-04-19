import sqlite3
import shutil
import re

def extract_name(raw_text, doc_hash):
    if not str(raw_text).strip():
        return f"미확인_{doc_hash[:8]}"
        
    # Analyze only first 200 chars
    prefix = raw_text[:200]
    
    # Simple regex for Korean names
    matches = re.findall(r'[가-힣]{2,4}(?=\s|$|\n|님|이력서|포트폴리오|경력단절|지원자|대리|과장|차장|부장|팀장|이사)', prefix)
    
    stop_words = {'컨설팅','컨설턴트','경력','신입','기획','개발','채용','마케팅','디자인','운영','영업','전략','재무','회계','인사','총무','개발자','엔지니어','데이터','분석','사업','관리','팀장','리더','매니저','매니져','지원','담당','담당자','자산','운용', '팀', '파트', '설계', '보안', '부문', '부문장', '기획팀', '개발팀', '운영팀', '경영', '정보', '솔루션', '포트', '폴리오', '이력서', '지원자', '프론트', '백엔드'}
    
    valid_matches = [m for m in matches if m not in stop_words and len(m) >= 2]
    
    if valid_matches:
        # Often the first match is the best if it's the title
        name = valid_matches[0]
        # Fallback to strip any whitespace
        name = name.strip()
        if len(name) >= 2:
            return name
            
    return f"미확인_{doc_hash[:8]}"

def recover():
    print("1. 백업 진행 중...")
    shutil.copy('candidates.db', 'candidates_backup_namefix.db')
    print("백업 완료: candidates_backup_namefix.db")
    
    conn = sqlite3.connect('candidates.db')
    cursor = conn.cursor()
    
    cursor.execute("SELECT id, document_hash, raw_text FROM candidates")
    rows = cursor.fetchall()
    
    print("\n2 & 3 & 4. 샘플 추출 확인 (처음 10건):")
    updates = []
    
    for row in rows:
        _id, doc_hash, raw_text = row
        if not raw_text: raw_text = ""
        if not doc_hash: doc_hash = "00000000"
        
        name = extract_name(raw_text, doc_hash)
        updates.append((name, _id))
    
    for i in range(min(10, len(updates))):
        print(f"ID: {updates[i][1][:8]}... | Hash: {rows[i][1][:8]} | Name: {updates[i][0]}")
        
    print(f"\n5. {len(updates)}건 전체 UPDATE 실행 중...")
    cursor.executemany("UPDATE candidates SET name_kr = ? WHERE id = ?", updates)
    conn.commit()
    print("UPDATE 완료.")
    
    print("\n6. 상위 이름 분포 (Top 10):")
    cursor.execute("SELECT name_kr, count(*) FROM candidates GROUP BY name_kr ORDER BY count(*) DESC LIMIT 10")
    for row in cursor.fetchall():
        print(f"'{row[0]}': {row[1]}명")
        
    conn.close()

if __name__ == "__main__":
    recover()
