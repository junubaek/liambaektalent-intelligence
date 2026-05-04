
import sqlite3
import re
import sys

# Set output encoding to utf-8
sys.stdout.reconfigure(encoding='utf-8')

def normalize_company(name):
    if not name:
        return ""
    # Remove common suffixes and prefixes
    name = re.sub(r'\(주\)|㈜|주식회사|\(재\)|\(사\)|Inc\.|Ltd\.|LLC|Co\.,\s*Ltd\.', '', name)
    # Remove spaces and lowercase
    name = re.sub(r'\s+', '', name).lower()
    return name

def enhanced_dedup():
    conn = sqlite3.connect('candidates.db')
    cur = conn.cursor()
    
    # 1. Get all candidates
    cur.execute("SELECT id, name_kr, current_company, LENGTH(COALESCE(raw_text, '')) as txt_len FROM candidates WHERE name_kr IS NOT NULL AND name_kr != ''")
    all_candidates = cur.fetchall()
    
    groups = {}
    for cid, name, company, txt_len in all_candidates:
        norm_company = normalize_company(company)
        key = (name, norm_company)
        if key not in groups:
            groups[key] = []
        groups[key].append({'id': cid, 'txt_len': txt_len, 'company': company})
    
    delete_ids = []
    kept_count = 0
    
    for key, cands in groups.items():
        if len(cands) > 1:
            # Sort by text length descending
            cands.sort(key=lambda x: x['txt_len'], reverse=True)
            # Keep the first one, delete the rest
            for redundant in cands[1:]:
                delete_ids.append(redundant['id'])
            kept_count += 1
        else:
            kept_count += 1
            
    print(f"Total candidate groups: {len(groups)}")
    print(f"Candidates to delete: {len(delete_ids)}")
    
    if delete_ids:
        # Delete in batches
        batch_size = 500
        for i in range(0, len(delete_ids), batch_size):
            batch = delete_ids[i:i+batch_size]
            cur.execute(f"DELETE FROM candidates WHERE id IN ({','.join(['?']*len(batch))})", batch)
        conn.commit()
        print("Deletion complete.")
        
    conn.close()

if __name__ == "__main__":
    enhanced_dedup()
