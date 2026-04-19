import sqlite3
import requests
import json
import re

def get_korean_name(raw_name):
    # Same proven logic but strict
    clean = re.sub(r'\[.*?\]', '', raw_name)
    clean = re.sub(r'\(.*?\)', '', clean)
    clean = re.sub(r'부문|원본|최종|포트폴리오|이력서|합격|이력|Resume|CV', '', clean, flags=re.IGNORECASE)
    matches = re.findall(r'[가-힣]{2,4}', clean)
    stop_words = {'컨설팅','컨설턴트','경력','신입','기획','개발','채용','마케팅','디자인','운영','영업','전략','재무','회계','인사','총무','데이터','분석','사업','관리','팀장','리더','매니저','매니져','지원','담당','담당자','자산','운용', '팀', '파트', '설계', '보안', '경영', '정보', '솔루션'}
    valid_matches = [m for m in matches if m not in stop_words and len(m) >= 2]
    return valid_matches[0] if valid_matches else "미확인"

def main():
    conn = sqlite3.connect('candidates.db')
    cur = conn.cursor()
    
    url = 'http://127.0.0.1:7474/db/neo4j/tx/commit'
    query = 'MATCH (c:Candidate) RETURN c.id, c.name'
    payload = {'statements': [{'statement': query}]}
    
    res = requests.post(url, json=payload, auth=('neo4j', 'toss1234'))
    if res.status_code != 200:
        print("Neo4j error:", res.text)
        return
        
    data = res.json()['results'][0]['data']
    print(f"Neo4j에서 {len(data)}명의 후보자 정보 수신 완료")
    
    updates = []
    neo4j_updates = []
    
    for row in data:
        doc_hash = row['row'][0]
        full_name = row['row'][1]
        
        name_kr = get_korean_name(full_name)
        if name_kr != "미확인":
            updates.append((name_kr, doc_hash))
        
    print("샘플 10개:")
    for i in range(min(10, len(updates))):
        print(f"  {updates[i][1][:8]}... -> {updates[i][0]}")

    print(f"총 {len(updates)}건 SQLite 업데이트 진행 중...")
    cur.executemany("UPDATE candidates SET name_kr = ? WHERE document_hash = ?", updates)
    conn.commit()
    
    print("\n상위 이름 분포 (Top 10):")
    cur.execute("SELECT name_kr, count(*) FROM candidates GROUP BY name_kr ORDER BY count(*) DESC LIMIT 10")
    for row in cur.fetchall():
        print(f"  '{row[0]}': {row[1]}명")
        
    conn.close()

if __name__ == "__main__":
    main()
