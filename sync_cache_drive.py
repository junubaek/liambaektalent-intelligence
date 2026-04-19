import json
import sqlite3

def main():
    print("Starting JSON Cache Sync for google_drive_url...")
    
    # 1. Get DB data
    conn = sqlite3.connect('candidates.db')
    c = conn.cursor()
    c.execute("SELECT id, google_drive_url FROM candidates WHERE is_duplicate=0 AND google_drive_url IS NOT NULL AND google_drive_url != '' AND google_drive_url != '#'")
    rows = c.fetchall()
    
    # Build dictionary
    url_map = {r[0]: r[1] for r in rows}
    print(f"Loaded {len(url_map)} URL mappings from SQLite.")
    
    # 2. Read cache
    with open('candidates_cache_jd.json', 'r', encoding='utf-8') as f:
        cache = json.load(f)
        
    print(f"Loaded {len(cache)} candidates from candidates_cache_jd.json.")
    
    # 3. Update cache
    updated_count = 0
    samples = []
    
    for cand in cache:
        cid = cand.get('id')
        if cid in url_map:
            new_url = url_map[cid]
            old_url = cand.get('google_drive_url')
            
            if old_url != new_url:
                cand['google_drive_url'] = new_url
                updated_count += 1
                
                # check if it's a newly added docs mapping for sampling
                if "docs.google.com" in new_url and len(samples) < 3:
                    samples.append({
                        "id": cid,
                        "name_kr": cand.get('name_kr'),
                        "google_drive_url": new_url
                    })
                    
    # 4. Save cache
    if updated_count > 0:
        with open('candidates_cache_jd.json', 'w', encoding='utf-8') as f:
            json.dump(cache, f, ensure_ascii=False, indent=2)
        print(f"✅ Successfully updated {updated_count} candidates in candidates_cache_jd.json")
    else:
        print("No candidates needed updating.")
        
    # fallback to find any 3 samples if updated_count didn't find specific ones
    if len(samples) < 3:
        for cand in cache:
            url = cand.get('google_drive_url', '')
            if url and "docs.google.com" in url:
                samples.append({
                    "id": cand.get("id"),
                    "name_kr": cand.get("name_kr"),
                    "google_drive_url": url
                })
                if len(samples) >= 3:
                    break
                    
    print("\n[docs.google.com 샘플 3명 확인]")
    for i, s in enumerate(samples):
        print(f"#{i+1}: {s['name_kr']} ({s['id']})\n   -> {s['google_drive_url']}")
        
    conn.close()

if __name__ == "__main__":
    main()
