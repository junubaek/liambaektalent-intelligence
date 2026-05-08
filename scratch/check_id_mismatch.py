import sqlite3
import json
import sys

# Set encoding for output to handle Korean characters in some environments
# But usually python handles it if the environment supports it.

def check_all_targets():
    with open('reparse_targets.json', 'r', encoding='utf-8') as f:
        targets = json.load(f)
        
    conn = sqlite3.connect('candidates.db')
    cursor = conn.cursor()
    
    print(f"Checking {len(targets)} targets in candidates.db...")
    
    for t in targets:
        name = t['name_kr']
        target_id = t['id']
        
        # Check by ID
        cursor.execute("SELECT id, name_kr FROM candidates WHERE id = ?", (target_id,))
        row = cursor.fetchone()
        
        if row:
            print(f"[FOUND BY ID] {name} ({target_id}) -> Matches in DB as {row[1]}")
        else:
            # Try finding by name
            cursor.execute("SELECT id, name_kr FROM candidates WHERE name_kr = ?", (name,))
            rows = cursor.fetchall()
            if rows:
                print(f"[ID MISMATCH] {name} (Target ID: {target_id})")
                for r in rows:
                    print(f"  - Found in DB with ID: {r[0]}")
            else:
                print(f"[NOT FOUND] {name} ({target_id}) not in DB.")
                
    conn.close()

if __name__ == "__main__":
    check_all_targets()
