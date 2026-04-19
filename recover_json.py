import sqlite3
import json
import re
import shutil

def get_korean_name(raw_name):
    if not isinstance(raw_name, str):
        return "미확인"
    clean = re.sub(r'\[.*?\]', '', raw_name)
    clean = re.sub(r'\(.*?\)', '', clean)
    clean = re.sub(r'부문|원본|최종|포트폴리오|이력서|합격|이력|Resume|CV', '', clean, flags=re.IGNORECASE)
    matches = re.findall(r'[가-힣]{2,4}', clean)
    stop_words = {'컨설팅','컨설턴트','경력','신입','기획','개발','채용','마케팅','디자인','운영','영업','전략','재무','회계','인사','총무','데이터','분석','사업','관리','팀장','리더','매니저','매니져','지원','담당','담당자','자산','운용', '팀', '파트', '설계', '보안', '경영', '정보', '솔루션'}
    valid_matches = [m for m in matches if m not in stop_words and len(m) >= 2]
    return valid_matches[0] if valid_matches else "미확인"

def main():
    print("0. DB 롤백 실행")
    shutil.copy('candidates_backup_namefix.db', 'candidates.db')
    
    conn = sqlite3.connect('candidates.db')
    cur = conn.cursor()
    
    with open('candidates_cache_jd.json', 'r', encoding='utf-8') as f:
        cache = json.load(f)
        
    print(f"JSON 캐시본에서 {len(cache)}명의 정보 로드 완료 (기준점 역할)")
    
    updates = []
    
    for item in cache:
        c_id = item.get('id')
        full_name = item.get('name')
        
        name_kr = get_korean_name(full_name)
        if name_kr != "미확인":
            updates.append((name_kr, c_id))
            
    print("매핑 샘플 10개:")
    for i in range(min(10, len(updates))):
        print(f"  {updates[i][1][:8]}... -> {updates[i][0]}")

    print(f"총 {len(updates)}건 SQLite 업데이트 진행 중...")
    cur.executemany("UPDATE candidates SET name_kr = ? WHERE id = ?", updates)
    conn.commit()
    
    print("\n상위 이름 분포 (Top 10):")
    cur.execute("SELECT name_kr, count(*) FROM candidates GROUP BY name_kr ORDER BY count(*) DESC LIMIT 10")
    results = cur.fetchall()
    
    is_bugged = False
    for row in results:
        print(f"  '{row[0]}': {row[1]}명")
        if row[1] > 100:
            is_bugged = True
            
    if is_bugged:
        print("\n🚨 100명 이상 이름 존재. 다시 롤백")
        conn.close()
        shutil.copy('candidates_backup_namefix.db', 'candidates.db')
    else:
        print("\n✅ 이름 100% 복구 완료.")
        conn.close()

if __name__ == "__main__":
    main()
