import sqlite3
import json

def analyze_candidates():
    conn = sqlite3.connect('candidates.db')
    conn.row_factory = sqlite3.Row
    
    ids = [
        '33522567-1b6f-81e4-8b23-f31b4bd5d1de',
        '535fa3b5-dd87-486d-8023-687308450f05',
        '32122567-1b6f-8124-b68d-e58d82237481',
        '33522567-1b6f-8143-90e5-cbc0bf53044b',
        '530e31e5-30ff-4c43-8dc6-e31ca5ceeecd'
    ]
    
    for cid in ids:
        row = conn.cursor().execute('SELECT id, name_kr, email, current_company, sector, raw_text FROM candidates WHERE id = ?', (cid,)).fetchone()
        if row:
            print(f"--- ID: {row['id']} ---")
            print(f"Name_KR (garbled): {row['name_kr']}")
            print(f"Email: {row['email']}")
            print(f"Current Company: {row['current_company']}")
            print(f"Sector: {row['sector']}")
            print("Raw Text Snippet:")
            # Print first 500 chars of raw_text to find name/company
            raw_text = row['raw_text'] if row['raw_text'] else ""
            print(raw_text[:500])
            print("\n")
            
    conn.close()

if __name__ == "__main__":
    analyze_candidates()
