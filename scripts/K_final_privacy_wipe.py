import sqlite3
import json
import re

def wipe_privacy_and_requeue():
    print("Finding remaining privacy pollution...")
    conn = sqlite3.connect("candidates.db")
    c = conn.cursor()
    
    with open('candidates_cache_jd.json', 'r', encoding='utf-8') as f:
        cache = json.load(f)
        
    cache_map = {str(item['id']).replace('-', ''): item for item in cache}
    
    valid_ids_rows = c.execute("SELECT id FROM candidates WHERE is_duplicate=0 AND is_parsed=1").fetchall()
    
    patterns = ['010-', '@gmail', '@naver', '@kakao', '@daum', '생년월일', '현 주소', '현주소', '연락처', '이력서', '이 력 서', 'linkedin.com', 'github.com']
    
    requeued_count = 0
    for row in valid_ids_rows:
        cid = row[0]
        cid_str = str(cid).replace('-', '')
        cinfo = cache_map.get(cid_str)
        if not cinfo: continue
        
        summary = cinfo.get('summary', '') or cinfo.get('profile_summary', '')
        if not summary: continue
        
        if any(p in summary for p in patterns):
            print(f"Privacy found in {cinfo.get('name_kr')}! Requeuing...")
            cinfo['summary'] = None
            c.execute("UPDATE candidates SET is_parsed=0 WHERE id=?", (cid,))
            requeued_count += 1
            
    if requeued_count > 0:
        with open('candidates_cache_jd.json', 'w', encoding='utf-8') as f:
            json.dump(cache, f, ensure_ascii=False, indent=2)
        conn.commit()
    conn.close()
    print(f"Requeued {requeued_count} candidates for parsing.")

if __name__ == "__main__":
    wipe_privacy_and_requeue()
