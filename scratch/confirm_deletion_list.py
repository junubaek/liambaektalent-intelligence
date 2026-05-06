import sqlite3
import json

def confirm_deletion():
    conn = sqlite3.connect('candidates.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # These are the candidates with no career patterns and likely garbled names/empty text
    query = """
    SELECT id, name_kr, email, length(raw_text) as text_len, google_drive_url
    FROM candidates 
    WHERE is_duplicate = 0 
      AND (careers_json IS NULL OR careers_json = '[]' OR careers_json = '')
    """
    rows = cursor.execute(query).fetchall()
    
    to_delete = []
    to_keep = []
    
    for row in rows:
        # If text is extremely short and name is garbled/missing, it's a safe delete candidate
        if (row['text_len'] is None or row['text_len'] < 100) and (row['email'] is None or row['email'] == ''):
            to_delete.append(dict(row))
        else:
            to_keep.append(dict(row))
            
    print(f"Safe to delete: {len(to_delete)}")
    print(f"Need further review (has email or long text): {len(to_keep)}")
    
    with open('candidates_to_delete.json', 'w', encoding='utf-8') as f:
        json.dump(to_delete, f, ensure_ascii=False, indent=2)
        
    for r in to_keep:
        print(f"KEEP: {r['name_kr']} ({r['email']}), Len: {r['text_len']}")

    conn.close()

if __name__ == "__main__":
    confirm_deletion()
