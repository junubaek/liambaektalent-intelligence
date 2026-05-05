import sqlite3
import json
import sys
sys.stdout.reconfigure(encoding='utf-8')

conn = sqlite3.connect('candidates.db')
cur = conn.cursor()

targets = ['이민지', '정소윤', '권슬기', '손민정', '김광우', '조예원', '남현승', '장현', '성장현', '마켓로보']

for name in targets:
    print(f"--- {name} ---")
    cur.execute("SELECT id, name_kr, current_company, profile_summary, google_drive_url, is_duplicate FROM candidates WHERE name_kr LIKE ?", (f'%{name}%',))
    rows = cur.fetchall()
    for r in rows:
        print(f"ID: {r[0]} | Name: {r[1]} | Company: {r[2]} | Dup: {r[5]}")
        print(f"URL: {r[4]}")
        # print(f"Summary: {r[3][:100]}...")
    print()

conn.close()
