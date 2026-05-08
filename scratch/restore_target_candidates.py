import sqlite3
import json

def restore_targets():
    with open('reparse_targets.json', 'r', encoding='utf-8') as f:
        targets = json.load(f)
        
    target_ids = [t['id'] for t in targets]
    
    source_conn = sqlite3.connect('candidates_reparsed_20260425_0230.db')
    dest_conn = sqlite3.connect('candidates.db')
    
    source_cursor = source_conn.cursor()
    dest_cursor = dest_conn.cursor()
    
    print(f"Restoring {len(target_ids)} targets...")
    
    for cid in target_ids:
        # Check if already exists in dest
        dest_cursor.execute("SELECT id FROM candidates WHERE id = ?", (cid,))
        if dest_cursor.fetchone():
            print(f"  [SKIP] Candidate {cid} already exists in candidates.db")
            continue
            
        # Get from source
        source_cursor.execute("SELECT * FROM candidates WHERE id = ?", (cid,))
        row = source_cursor.fetchone()
        
        if row:
            # Get column names
            columns = [description[0] for description in source_cursor.description]
            placeholders = ', '.join(['?'] * len(row))
            col_names = ', '.join(columns)
            
            query = f"INSERT INTO candidates ({col_names}) VALUES ({placeholders})"
            try:
                dest_cursor.execute(query, row)
                print(f"  [RESTORED] Candidate {cid} ({row[columns.index('name_kr')]})")
            except Exception as e:
                print(f"  [ERROR] Failed to restore {cid}: {e}")
        else:
            print(f"  [NOT FOUND] Candidate {cid} not found in source DB.")
            
    dest_conn.commit()
    source_conn.close()
    dest_conn.close()
    print("Restore complete.")

if __name__ == "__main__":
    restore_targets()
