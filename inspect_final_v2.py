import sqlite3
import sys
sys.stdout.reconfigure(encoding='utf-8')

conn = sqlite3.connect('candidates.db')
cur = conn.cursor()

targets = ['홍주영', '이재구', '김병환', '이영도', '신권철', '정한아', '김승현', '장현', '성장현', '이민지', '윤정민', '이정우']

print("--- Candidate Status ---")
for name in targets:
    cur.execute("SELECT id, name_kr, current_company, is_duplicate, google_drive_url FROM candidates WHERE name_kr LIKE ?", (f'%{name}%',))
    rows = cur.fetchall()
    print(f"\nTarget: {name}")
    if not rows:
        print("  Not Found")
    for r in rows:
        print(f"  ID: {r[0]} | Name: {r[1]} | Company: {r[2]} | Dup: {r[3]} | URL: {'Yes' if r[4] else 'No'}")

# Special check for Kakao Unknown
print("\n--- Special Check: Kakao ---")
cur.execute("SELECT id, name_kr, current_company, is_duplicate FROM candidates WHERE current_company LIKE '%kakao%' OR raw_text LIKE '%kakao%'")
rows = cur.fetchall()
for r in rows:
    if '미상' in r[1] or not r[1]:
        print(f"  ID: {r[0]} | Name: {r[1]} | Company: {r[2]} | Dup: {r[3]}")

conn.close()
