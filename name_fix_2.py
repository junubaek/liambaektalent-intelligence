import sqlite3
import re

def fix_corrupted_names():
    conn = sqlite3.connect('candidates.db')
    cur = conn.cursor()
    
    stop_words = ('자금', '기획', '개발', '운영', '마케팅', '재무', '회계', '전략', '인사', '총무', '법무')
    
    query = f"SELECT id, name_kr, substr(raw_text, 1, 300) FROM candidates WHERE name_kr IN {stop_words} OR length(name_kr) > 10"
    cur.execute(query)
    rows = cur.fetchall()
    
    updates = []
    
    for r in rows:
        cid, current_name, raw_prefix = r
        
        lines = [line.strip() for line in raw_prefix.split('\n') if line.strip()]
        new_name = current_name
        
        if len(lines) > 0:
            first_line = lines[0]
            # More relaxed regex for finding isolated Korean names (2-4 chars)
            # Maybe the name is just exactly "홍길동" or followed by something
            match = re.search(r'([가-힣]{2,4})(?:이력서|포트폴리오|님의|님|지원자|대리|과장|팀장|차장|부장|사원|선임|책임|수석|이사|대표|상무|전무|부사장|사장|_|\s*\()', first_line)
            
            if match:
                extracted = match.group(1)
                if extracted not in stop_words and not any(w in extracted for w in ['이력서', '포트폴리오', '경력기술서', '클라우드', '소프트웨어', '디지털', '플랫폼', '서비스', '솔루션']):
                    new_name = extracted
            else:
                # Fallback, just look for any 3-char Korean word at the very beginning
                match2 = re.match(r'^([가-힣]{2,4})', first_line)
                if match2:
                    extracted2 = match2.group(1)
                    if extracted2 not in stop_words and not any(w in extracted2 for w in ['이력서', '경력', '연락처', '프로필', '클라우드']):
                        new_name = extracted2
                        
        if new_name != current_name and len(new_name) <= 4:
            updates.append((new_name, cid))
            
    print(f"Updates prepared for {len(updates)} out of {len(rows)} records.")
    
    for u in updates:
        cur.execute("UPDATE candidates SET name_kr = ? WHERE id = ?", (u[0], u[1]))
        
    conn.commit()
    conn.close()
    print("Done applying updates.")

if __name__ == "__main__":
    fix_corrupted_names()
