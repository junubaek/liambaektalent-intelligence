import sqlite3
import json
import re

def cleanse_privacy():
    print("Starting Privacy Cleansing (Phase 1)...")
    
    conn = sqlite3.connect("candidates.db")
    c = conn.cursor()
    
    # 1. Load cache
    cache_path = 'candidates_cache_jd.json'
    with open(cache_path, 'r', encoding='utf-8') as f:
        cache = json.load(f)
        
    # Get active valid IDs from SQLite
    valid_ids_rows = c.execute("SELECT id, document_hash FROM candidates WHERE is_duplicate=0").fetchall()
    valid_id_map = {str(r[0]).replace('-', ''): r[1] for r in valid_ids_rows}
    
    # 2. Define Patterns
    patterns = [
        r'010-',
        r'@gmail', r'@naver', r'@kakao', r'@daum', r'@nate', r'@hanmail',
        r'생년월일',
        r'현 주소', r'현주소',
        r'이 력 서', r'이력서',
        r'linkedin\.com',
        r'연 락 처', r'연락처:',
        r'\(만 \d+세\)'
    ]
    
    # Github should only trigger if it's near the start
    github_pattern = r'^.{0,150}github\.com'
    
    cleared_count = 0
    updated_cache = False
    
    for item in cache:
        cid_clean = str(item['id']).replace('-', '')
        if cid_clean not in valid_id_map:
            continue
            
        summary = item.get('summary', '') or item.get('profile_summary', '')
        if not summary or not isinstance(summary, str) or summary == '정보 없음':
            continue
            
        needs_clear = False
        for p in patterns:
            if re.search(p, summary, re.IGNORECASE):
                needs_clear = True
                break
                
        if not needs_clear and re.search(github_pattern, summary, re.IGNORECASE):
            needs_clear = True
            
        if needs_clear:
            item['summary'] = None
            item['profile_summary'] = None
            updated_cache = True
            
            # Reset is_parsed to 0 in SQLite
            doc_hash = valid_id_map[cid_clean]
            c.execute("UPDATE candidates SET is_parsed=0 WHERE document_hash=?", (doc_hash,))
            cleared_count += 1
            
    if updated_cache:
        with open(cache_path, 'w', encoding='utf-8') as f:
            json.dump(cache, f, ensure_ascii=False, indent=2)
            
    conn.commit()
    print(f"Successfully cleared {cleared_count} summaries and moved them to re-parsing queue!")
    conn.close()

if __name__ == "__main__":
    cleanse_privacy()
