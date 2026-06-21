import sqlite3
conn = sqlite3.connect('candidates.db')
cur = conn.cursor()
cur.execute('DELETE FROM candidates')
cur.execute('DELETE FROM sqlite_sequence WHERE name="candidates"')
conn.commit()
cur.execute('SELECT COUNT(*) FROM candidates')
print('초기화 완료. 남은 레코드:', cur.fetchone()[0])
conn.close()
