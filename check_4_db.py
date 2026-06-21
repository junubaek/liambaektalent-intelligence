import sqlite3

conn = sqlite3.connect(r'C:\Users\cazam\Downloads\이력서자동분석검색시스템\candidates.db')
cur = conn.cursor()

names = ['김태경', '오수영', '김형수', '박천혁']
for name in names:
    cur.execute("SELECT id, name_kr, email, phone, is_duplicate, source_file, current_company FROM candidates WHERE name_kr LIKE ?", (f"%{name}%",))
    print(f"=== {name} ===")
    for row in cur.fetchall():
        print(f"ID: {row[0]} | Name: {row[1]} | Email: {row[2]} | Phone: {row[3]} | IsDup: {row[4]} | File: {row[5]} | Company: {row[6]}")
conn.close()
