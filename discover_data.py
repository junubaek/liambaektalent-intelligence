import sqlite3
import sys
sys.stdout.reconfigure(encoding='utf-8')

conn = sqlite3.connect('candidates.db')
cur = conn.cursor()

targets = ['김승현', '이영도', '신권철', '김병환', '이재구', '홍주영', '이정우', '윤정민']

print("--- Data Discovery Results ---")
for t in targets:
    cur.execute("SELECT id, name_kr, current_company, is_duplicate FROM candidates WHERE raw_text LIKE ?", (f'%{t}%',))
    rows = cur.fetchall()
    print(f"\nTarget: {t}")
    for r in rows:
        print(f"  ID: {r[0]} | Name: {r[1]} | Company: {r[2]} | Dup: {r[3]}")

conn.close()
