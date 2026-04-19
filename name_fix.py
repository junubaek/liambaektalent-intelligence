import sqlite3
import re
import json

def fix_corrupted_names():
    conn = sqlite3.connect('candidates.db')
    cur = conn.cursor()
    
    stop_words = ('자금', '기획', '개발', '운영', '마케팅', '재무', '회계', '전략', '인사', '총무', '법무')
    
    query = f"SELECT id, name_kr, substr(raw_text, 1, 200) FROM candidates WHERE name_kr IN {stop_words} OR length(name_kr) > 10"
    cur.execute(query)
    rows = cur.fetchall()
    
    print(f"Total rows to fix: {len(rows)}")
    
    updates = []
    
    for r in rows:
        cid, current_name, raw_prefix = r
        
        # Look for explicit [Name_Resume.pdf] or similar patterns at the top of raw_text.
        # It's usually something like "홍길동_이력서.pdf" or "1. 홍길동님 이력서"
        # Since it's raw_text from Notion, the Title is often the first line.
        lines = raw_prefix.split('\n')
        
        new_name = current_name
        
        # Heuristic 1: Extract from the first line which is usually the title.
        if len(lines) > 0:
            first_line = lines[0].strip()
            # Regex to find a typical Korean name (2 to 4 letters) before any suffix
            # e.g. "홍길동 이력서", "홍길동_포트폴리오", "김철수(마케팅)"
            match = re.search(r'^([가-힣]{2,4})(?:[_\s\(\[]?(?:이력서|포트폴리오|경력기술서|이력|님|과장|대리|팀장|차장|부장|대표|이사|상무|전무|부사장|사장|의|수석|책임|선임|전임|사원|지원자|\(.*\)))', first_line)
            
            if match:
                extracted = match.group(1)
                # Check if extracted is not a stop word itself
                if extracted not in stop_words and len(extracted) <= 4:
                    new_name = extracted
            else:
                # Alternatively just taking the first 2-3 letters of the first line if it looks like a name
                match2 = re.match(r'^([가-힣]{2,4})', first_line)
                if match2:
                    extracted2 = match2.group(1)
                    if extracted2 not in stop_words and len(extracted2) <= 4:
                        new_name = extracted2
                        
        if new_name != current_name and new_name not in stop_words:
            updates.append((new_name, cid))
            
    print(f"Updates prepared for {len(updates)} records.")
    
    for r in updates[:5]:
        print(f"Will change to: {r[0]} for ID: {r[1]}")
        
    print("Applying updates...")
    for u in updates:
        cur.execute("UPDATE candidates SET name_kr = ? WHERE id = ?", (u[0], u[1]))
        
    conn.commit()
    conn.close()
    print("Done applying updates.")

if __name__ == "__main__":
    fix_corrupted_names()
