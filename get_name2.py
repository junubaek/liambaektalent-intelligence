import sqlite3
import json

db_path = 'candidates.db'
conn = sqlite3.connect(db_path)
conn.row_factory = sqlite3.Row
cur = conn.cursor()

cur.execute("SELECT * FROM candidates WHERE id = '32022567-1b6f-81cf-af18-cbdada2eecf0'")
row = cur.fetchone()
if row:
    d = dict(row)
    print("KEYS IN SQLITE:", list(d.keys()))
    
    if 'raw_text' in d and d['raw_text']:
        # Dump first 500 chars of raw text to see if there's a name
        text = d['raw_text'][:500].encode('utf-8', 'ignore').decode('utf-8')
        print("RAW TEXT SNIPPET:\\n", text)
        
    if 'original_filename' in d:
        print("Original Filename:", d.get('original_filename', 'N/A').encode('utf-8', 'ignore').decode('utf-8'))
        
    if 'parsed_career_json' in d:
        print("Careers:", d.get('parsed_career_json', '')[:200])

conn.close()
