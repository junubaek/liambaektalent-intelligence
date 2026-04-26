import sqlite3
import json

db_path = 'candidates.db'
conn = sqlite3.connect(db_path)
conn.row_factory = sqlite3.Row
cur = conn.cursor()

cur.execute("SELECT * FROM candidates WHERE id = '32022567-1b6f-81cf-af18-cbdada2eecf0'")
row = cur.fetchone()

with open('output_debug.txt', 'w', encoding='utf-8') as f:
    if row:
        d = dict(row)
        f.write(f"ID: {d['id']}\n")
        f.write(f"Name_KR: {d['name_kr']}\n")
        f.write(f"Email: {d['email']}\n")
        f.write(f"Phone: {d['phone']}\n")
        f.write(f"Google Drive URL: {d['google_drive_url']}\n")
        f.write(f"Current Company: {d['current_company']}\n")
        
        if 'raw_text' in d and d['raw_text']:
            text = d['raw_text'][:1000]
            f.write(f"\nRAW TEXT SNIPPET:\n{text}\n")
            
        if 'careers_json' in d and d['careers_json']:
            f.write(f"\nCareers:\n{d['careers_json'][:500]}")
    else:
        f.write("Not found in SQLite.")

conn.close()
