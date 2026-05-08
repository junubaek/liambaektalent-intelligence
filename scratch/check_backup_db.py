import sqlite3
import json

def check_other_db():
    with open('reparse_targets.json', 'r', encoding='utf-8') as f:
        targets = json.load(f)
        
    conn = sqlite3.connect('candidates_reparsed_20260425_0230.db')
    cursor = conn.cursor()
    
    print(f"Checking {len(targets)} targets in candidates_reparsed_20260425_0230.db...")
    
    for t in targets:
        name = t['name_kr']
        target_id = t['id']
        
        cursor.execute("SELECT id, name_kr FROM candidates WHERE name_kr = ?", (name,))
        rows = cursor.fetchall()
        if rows:
            print(f"[FOUND] {name} (Target ID: {target_id})")
            for r in rows:
                print(f"  - Found with ID: {r[0]}")
        else:
            print(f"[NOT FOUND] {name} ({target_id})")
                
    conn.close()

if __name__ == "__main__":
    check_other_db()
