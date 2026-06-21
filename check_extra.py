import sqlite3

conn = sqlite3.connect(r'C:\Users\cazam\Downloads\이력서자동분석검색시스템\candidates.db')
cur = conn.cursor()

ids = ['33522567-1b6f-81c1-9551-da57bc7d27c7', '341e6ee6-cc8b-49ef-8bfd-6b5883ec3dbf']
for cid in ids:
    cur.execute("SELECT id, name_kr, email, phone, is_duplicate, current_company, profile_summary FROM candidates WHERE id = ?", (cid,))
    row = cur.fetchone()
    if row:
        summary_str = row[6][:100] if row[6] else "None"
        print(f"ID: {row[0]} | Name: {row[1]} | Email: {row[2]} | Phone: {row[3]} | IsDup: {row[4]} | Company: {row[5]} | Summary: {summary_str}")
    else:
        print(f"ID {cid} not found in SQLite.")
conn.close()
