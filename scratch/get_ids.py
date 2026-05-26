import sqlite3, sys
sys.stdout.reconfigure(encoding='utf-8')
conn = sqlite3.connect('candidates.db')
cur = conn.cursor()
cur.execute("SELECT id, current_company, name_kr FROM candidates WHERE name_kr = '이상헌'")
for r in cur.fetchall():
    print(f"{r[0]} | {r[1]} | {r[2]}")
conn.close()
