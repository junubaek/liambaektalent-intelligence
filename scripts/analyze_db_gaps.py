import json
import sqlite3

def analyze_gaps():
    conn = sqlite3.connect('candidates.db')
    c = conn.cursor()
    c.execute("SELECT id, name_kr, email, phone, birth_year, education_json, careers_json, raw_text FROM candidates")
    db_rows = c.fetchall()
    
    with open('candidates_cache_jd.json', 'r', encoding='utf-8') as f:
        cache = json.load(f)
        
    cache_map = {str(item['id']).replace('-', ''): item for item in cache}
    
    stats = {
        'total_db': len(db_rows),
        'total_cache': len(cache),
        'missing_email': 0,
        'missing_phone': 0,
        'missing_education': 0,
        'missing_careers': 0,
        'missing_summary_cache': 0
    }
    
    for row in db_rows:
        cid, name, email, phone, birth, edu, career, raw = row
        cid_clean = cid.replace('-', '')
        
        if not email or email.strip() == '': stats['missing_email'] += 1
        if not phone or phone.strip() == '': stats['missing_phone'] += 1
        
        edus = []
        try: edus = json.loads(edu) if edu else []
        except: pass
        if not edus: stats['missing_education'] += 1
        
        careers = []
        try: careers = json.loads(career) if career else []
        except: pass
        if not careers: stats['missing_careers'] += 1
        
        cache_item = cache_map.get(cid_clean, {})
        summary = cache_item.get('profile_summary', '')
        if not summary or summary.strip() == '':
            stats['missing_summary_cache'] += 1
            
    print(json.dumps(stats, indent=2))

if __name__ == "__main__":
    analyze_gaps()
