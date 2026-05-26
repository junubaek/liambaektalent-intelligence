import sqlite3, sys
sys.stdout.reconfigure(encoding='utf-8')

conn = sqlite3.connect('candidates.db')
cur = conn.cursor()

# Get all Lee Sang-heon records
cur.execute("SELECT id, name_kr, current_company, is_duplicate, profile_summary FROM candidates WHERE name_kr = '이상헌'")
rows = cur.fetchall()

print("--- 이상헌 레코드 상세 ---")
for r in rows:
    print(f"ID: {r[0]}")
    print(f"회사: {r[2]}")
    print(f"중복: {r[3]}")
    print(f"요약: {r[4]}")
    
    # Check if there's any field indicating what it's a duplicate of? 
    # Usually we don't have that in SQLite, but we can check the logic.
    
    # Let's check the raw_text first few lines to distinguish
    cur.execute("SELECT raw_text FROM candidates WHERE id = ?", (r[0],))
    raw = cur.fetchone()[0]
    print(f"Raw Text (처음 200자): {raw[:200].replace('\\n', ' ')}")
    print("-" * 50)

conn.close()
