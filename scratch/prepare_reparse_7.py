import sqlite3
import json

def prepare_reparse():
    conn = sqlite3.connect('candidates.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Target 7 records that are most likely the ones that failed
    query = """
    SELECT id, name_kr, email, google_drive_url, raw_text
    FROM candidates 
    WHERE is_duplicate = 0 
      AND (careers_json IS NULL OR careers_json = '[]' OR careers_json = '')
    LIMIT 10
    """
    rows = cursor.execute(query).fetchall()
    
    targets = []
    for row in rows:
        targets.append(dict(row))
        
    print(f"Identified {len(targets)} targets for re-parsing.")
    with open('reparse_targets.json', 'w', encoding='utf-8') as f:
        json.dump(targets, f, ensure_ascii=False, indent=2)
        
    conn.close()

if __name__ == "__main__":
    prepare_reparse()
