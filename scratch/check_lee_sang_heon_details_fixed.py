import sqlite3, sys
sys.stdout.reconfigure(encoding='utf-8')

conn = sqlite3.connect('candidates.db')
cur = conn.cursor()

# Get all Lee Sang-heon records
cur.execute("SELECT id, name_kr, current_company, is_duplicate, profile_summary FROM candidates WHERE name_kr = '이상헌'")
rows = cur.fetchall()

print("--- 이상헌 레코드 상세 ---")
for r in rows:
    summary = r[4] if r[4] else "N/A"
    print(f"ID: {r[0]}")
    print(f"회사: {r[2]}")
    print(f"중복: {r[3]}")
    print(f"요약: {summary[:100]}...")
    
    cur.execute("SELECT raw_text FROM candidates WHERE id = ?", (r[0],))
    raw_fetch = cur.fetchone()
    raw = raw_fetch[0] if raw_fetch else ""
    # Avoid backslash in f-string expression
    raw_clean = raw[:300].replace('\n', ' ').replace('\r', ' ')
    print(f"Raw Text: {raw_clean}")
    print("-" * 50)

conn.close()
