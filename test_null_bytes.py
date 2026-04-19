import sqlite3
conn = sqlite3.connect(r'C:\Users\cazam\Downloads\이력서자동분석검색시스템\candidates.db')
c = conn.cursor()
c.execute("SELECT name_kr, length(raw_text), raw_text FROM candidates WHERE name_kr IN ('안유리', '전진수')")
for row in c.fetchall():
    print('Name:', row[0], 'Length:', row[1])
    print('Repr:', repr(row[2][:50]))
