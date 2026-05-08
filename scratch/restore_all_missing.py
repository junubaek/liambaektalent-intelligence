import sqlite3
import json

def restore_all_missing():
    with open('scratch/remaining_targets.json', 'r', encoding='utf-8') as f:
        targets = json.load(f)
    
    missing_ids = [t['id'] for t in targets if t['text_len'] == 0 and t['is_parsed'] == 0]
    
    if not missing_ids:
        print("No missing IDs to restore.")
        return
    
    source_conn = sqlite3.connect('candidates_reparsed_20260425_0230.db')
    dest_conn = sqlite3.connect('candidates.db')
    
    source_cursor = source_conn.cursor()
    dest_cursor = dest_conn.cursor()
    
    restored = 0
    not_found = 0
    
    print(f"Restoring {len(missing_ids)} missing candidates from backup DB...")
    
    for cid in missing_ids:
        # Check if already exists
        dest_cursor.execute("SELECT id FROM candidates WHERE id = ?", (cid,))
        if dest_cursor.fetchone():
            continue
            
        source_cursor.execute("SELECT * FROM candidates WHERE id = ?", (cid,))
        row = source_cursor.fetchone()
        
        if row:
            columns = [desc[0] for desc in source_cursor.description]
            placeholders = ', '.join(['?'] * len(row))
            col_names = ', '.join(columns)
            
            try:
                dest_cursor.execute(f"INSERT INTO candidates ({col_names}) VALUES ({placeholders})", row)
                name_idx = columns.index('name_kr') if 'name_kr' in columns else None
                name = row[name_idx] if name_idx is not None else '?'
                print(f"  [RESTORED] {name} ({cid[:12]}...)")
                restored += 1
            except Exception as e:
                print(f"  [ERROR] {cid}: {e}")
        else:
            # Try to find by name in source DB
            target = next((t for t in targets if t['id'] == cid), None)
            if target:
                name = target['name_kr']
                source_cursor.execute("SELECT id, name_kr FROM candidates WHERE name_kr = ?", (name,))
                found = source_cursor.fetchall()
                if found:
                    print(f"  [FOUND BY NAME] {name} -> {found[0][0]} (ID mismatch)")
                else:
                    print(f"  [NOT FOUND] {name} ({cid}) not in backup DB either")
                    not_found += 1
    
    dest_conn.commit()
    source_conn.close()
    dest_conn.close()
    
    print(f"\n--- Restore Complete ---")
    print(f"  Restored: {restored}")
    print(f"  Not found: {not_found}")

if __name__ == "__main__":
    restore_all_missing()
