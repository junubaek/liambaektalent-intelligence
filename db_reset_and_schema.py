import sqlite3, sys
sys.stdout.reconfigure(encoding='utf-8')
conn = sqlite3.connect('candidates.db')
cur = conn.cursor()

# 전체 초기화
cur.execute('DELETE FROM candidates')
print('candidates 초기화 완료')

# current_title 컬럼 추가
try:
    cur.execute('ALTER TABLE candidates ADD COLUMN current_title TEXT')
    print('current_title 컬럼 추가됨')
except Exception as e:
    print('current_title 이미 존재')

conn.commit()
cur.execute('SELECT COUNT(*) FROM candidates')
print('현재 레코드:', cur.fetchone()[0])
conn.close()
