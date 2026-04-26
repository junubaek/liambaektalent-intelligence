import sqlite3
import json

db_path = 'candidates.db'
conn = sqlite3.connect(db_path)
conn.row_factory = sqlite3.Row
cur = conn.cursor()

print("\n--- Checking 서버 ---")
cur.execute("SELECT id, name_kr, google_drive_url, raw_text FROM candidates WHERE name_kr = '서버'")
for row in cur.fetchall():
    d = dict(row)
    print(f"ID: {d['id']}")
    print(f"Google Drive URL: {d.get('google_drive_url', 'N/A')}")
    if d.get('raw_text'):
        try:
            print("RAW TEXT Snippet:", d['raw_text'][:200].encode('utf-8', 'ignore').decode('utf-8'))
        except:
            pass

conn.close()
