import sqlite3
import json

def find_failed_7():
    conn = sqlite3.connect('candidates.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # We want records that were attempted but didn't result in careers_json or have errors
    # In my script, I didn't update is_parsed=1 if it failed completely.
    # But some might have 'OK' but empty JSON.
    
    print("=== Failed/Incomplete Records from Latest Batch ===")
    
    # Search for records updated in the last 1 hour that have issues
    query = """
    SELECT id, name_kr, email, last_error, careers_json, raw_text
    FROM candidates 
    WHERE updated_at > datetime('now', '-1 hour')
      AND (careers_json IS NULL OR careers_json = '[]' OR careers_json = '')
    """
    rows = cursor.fetchall()
    
    for row in rows:
        print(f"ID: {row['id']}")
        print(f"Name: {row['name_kr']}")
        print(f"Email: {row['email']}")
        print(f"Last Error: {row['last_error']}")
        # Check text length to see if it's empty
        text_len = len(row['raw_text']) if row['raw_text'] else 0
        print(f"Text Length: {text_len}")
        print("-" * 20)
        
    conn.close()

if __name__ == "__main__":
    find_failed_7()
