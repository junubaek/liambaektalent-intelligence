import sqlite3

conn = sqlite3.connect(r'C:\Users\cazam\Downloads\이력서자동분석검색시스템\candidates.db')
c = conn.cursor()
c.execute("SELECT raw_text FROM candidates WHERE name_kr='안유리'")
res = c.fetchone()
if res:
    raw_text = res[0]
    clean_text = raw_text.replace('\x00', '')
    print('Cleaned length:', len(clean_text))
    print(clean_text[:500])
