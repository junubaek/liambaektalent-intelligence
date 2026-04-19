import sqlite3
import json

def run_sqlite_dedup():
    print("Connecting to candidates.db...")
    conn = sqlite3.connect('candidates.db')
    c = conn.cursor()
    
    # 1. Add columns if not exist
    try:
        c.execute("ALTER TABLE candidates ADD COLUMN is_duplicate INTEGER DEFAULT 0")
        print("Added is_duplicate column.")
    except sqlite3.OperationalError:
        print("Column is_duplicate already exists.")
        
    try:
        c.execute("ALTER TABLE candidates ADD COLUMN duplicate_of TEXT DEFAULT NULL")
        print("Added duplicate_of column.")
    except sqlite3.OperationalError:
        print("Column duplicate_of already exists.")
        
    # Reset all to 0 first (in case of re-run)
    c.execute("UPDATE candidates SET is_duplicate = 0, duplicate_of = NULL")
    
    # Load cache data for scoring
    with open('candidates_cache_jd.json', 'r', encoding='utf-8') as f:
        cache = json.load(f)
    cache_map = {str(item['id']).replace('-', ''): item for item in cache}
    
    # 2. Fetch all candidates to calculate scores
    c.execute("SELECT id, name_kr, document_hash, email, phone, birth_year FROM candidates")
    rows = c.fetchall()
    
    grouped_by_name = {}
    for row in rows:
        cid, name_kr, doc_hash, email, phone, birth_year = row
        cid_clean = str(cid).replace('-', '')
        
        # We need a fallback if name_kr is empty
        if not name_kr: name_kr = "EMPTY_NAME"
        
        cdata = cache_map.get(cid_clean, {})
        summary = cdata.get('summary', '') or cdata.get('profile_summary', '')
        company = cdata.get('current_company', '')
        sector = cdata.get('sector', '')
        
        score = 0
        # - summary IS NOT NULL AND != '정보 없음' AND != '' → +2
        if summary and summary.strip() != '' and summary != '정보 없음' and summary != ' ':
            score += 2
        # - current_company IS NOT NULL AND != '미상' AND != '' → +2
        if company and company.strip() != '' and company != '미상' and company != '̻':
            score += 2
        # - birth_year IS NOT NULL → +1
        if birth_year:
            score += 1
        # - email IS NOT NULL AND != '' → +1
        if email and email.strip() != '':
            score += 1
        # - phone IS NOT NULL AND != '' → +1
        if phone and phone.strip() != '':
            score += 1
        # - sector IS NOT NULL AND != '미분류' AND != '' → +1
        if sector and sector.strip() != '' and sector != '미분류' and sector != 'з':
            score += 1
            
        grouped_by_name.setdefault(name_kr, []).append({
            'id': cid,
            'doc_hash': doc_hash,
            'score': score
        })
        
    # 3. Mark duplicates
    total_dedup = 0
    for name, group in grouped_by_name.items():
        if len(group) <= 1: continue # No duplicates
        
        # Sort by score descending
        group.sort(key=lambda x: x['score'], reverse=True)
        
        best = group[0]
        # Mark all others as duplicates
        for dup in group[1:]:
            c.execute("UPDATE candidates SET is_duplicate = 1, duplicate_of = ? WHERE id = ?", (best['doc_hash'], dup['id']))
            total_dedup += 1
            
    conn.commit()
    print(f"Total duplicates marked in SQLite: {total_dedup}")
    
    # 4. Verify uniqueness
    res = c.execute("SELECT name_kr, count(*) as cnt FROM candidates WHERE is_duplicate=0 GROUP BY name_kr HAVING cnt > 1 ORDER BY cnt DESC LIMIT 1").fetchall()
    if res:
        print("WARNING! Found names with cnt > 1 despite dedup:")
        print(res)
    else:
        print("Success: 0 duplicates strictly sharing the same exact name_kr remaining.")
        
if __name__ == "__main__":
    run_sqlite_dedup()
