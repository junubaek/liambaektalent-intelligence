import sqlite3
import json

db_path = 'candidates.db'
conn = sqlite3.connect(db_path)
conn.row_factory = sqlite3.Row
cur = conn.cursor()

print("--- Checking 김별 ---")
cur.execute("SELECT id, name_kr, phone FROM candidates WHERE name_kr = '김별'")
for row in cur.fetchall():
    print(f"ID: {row['id']}, Name: {row['name_kr'].encode('utf-8', 'ignore').decode('utf-8')}, Phone: {row['phone']}")

print("\n--- Checking 서버 ---")
cur.execute("SELECT id, name_kr, google_drive_url, original_filename FROM candidates WHERE name_kr = '서버'")
for row in cur.fetchall():
    d = dict(row)
    print(f"ID: {d['id']}")
    print(f"Name_KR: {d['name_kr'].encode('utf-8', 'ignore').decode('utf-8')}")
    print(f"Original Filename: {d.get('original_filename', 'N/A')}")
    print(f"Google Drive URL: {d.get('google_drive_url', 'N/A')}")

conn.close()
