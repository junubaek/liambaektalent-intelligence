import sqlite3
import json

def check_current_status():
    with open('candidates_to_delete.json', 'r', encoding='utf-8') as f:
        all_targets = json.load(f)
    
    conn = sqlite3.connect('candidates.db')
    cursor = conn.cursor()
    
    print(f"Total targets in candidates_to_delete.json: {len(all_targets)}")
    
    found = 0
    missing = 0
    parsed_ok = 0
    needs_work = []
    
    for t in all_targets:
        cid = t['id']
        name = t['name_kr']
        
        cursor.execute("""
            SELECT id, name_kr, is_parsed, total_years, sector, 
                   LENGTH(raw_text) as text_len, LENGTH(profile_summary) as summary_len
            FROM candidates WHERE id = ?
        """, (cid,))
        row = cursor.fetchone()
        
        if row:
            found += 1
            is_parsed = row[2]
            text_len = row[5] or 0
            summary_len = row[6] or 0
            sector = row[4] or ''
            
            if is_parsed and text_len > 200 and summary_len > 10:
                parsed_ok += 1
                status = "OK"
            else:
                needs_work.append({
                    'id': cid, 
                    'name_kr': name, 
                    'google_drive_url': t.get('google_drive_url', ''),
                    'text_len': text_len,
                    'is_parsed': is_parsed
                })
                status = f"NEEDS WORK (text={text_len}, parsed={is_parsed}, sector='{sector}')"
            print(f"  [{status}] {name} ({cid[:12]}...)")
        else:
            missing += 1
            needs_work.append({
                'id': cid, 
                'name_kr': name, 
                'google_drive_url': t.get('google_drive_url', ''),
                'text_len': 0,
                'is_parsed': 0
            })
            print(f"  [MISSING FROM DB] {name} ({cid[:12]}...)")
    
    print(f"\n--- Summary ---")
    print(f"Found in DB:    {found}/{len(all_targets)}")
    print(f"Missing from DB:{missing}/{len(all_targets)}")
    print(f"Fully parsed:   {parsed_ok}/{found}")
    print(f"Needs work:     {len(needs_work)}")
    
    # Save needs_work list
    with open('scratch/remaining_targets.json', 'w', encoding='utf-8') as f:
        json.dump(needs_work, f, ensure_ascii=False, indent=2)
    print(f"\nSaved {len(needs_work)} remaining targets to scratch/remaining_targets.json")
    
    conn.close()

if __name__ == "__main__":
    check_current_status()
