import sqlite3, sys
sys.stdout.reconfigure(encoding='utf-8')
conn = sqlite3.connect('candidates.db')
cur = conn.cursor()

# 1. 이범기, 노장훈 — 깡통 마스터 삭제 + 진짜 데이터 승격
cur.execute('DELETE FROM candidates WHERE id LIKE "32f22567%" AND name_kr="이범기"')
cur.execute('UPDATE candidates SET is_duplicate=0 WHERE id LIKE "ba90c498%"')
cur.execute('DELETE FROM candidates WHERE id LIKE "31f22567%" AND name_kr="노장훈"')
cur.execute('UPDATE candidates SET is_duplicate=0 WHERE id LIKE "1f2f47ca%"')

# 2. 파편 데이터 삭제 — 500자 미만 쓰레기 제거
for name, keep_company in [
    ('이규원', '대방건설㈜'),
    ('하정근', '㈜야놀자'),
    ('이효성', '대방건설㈜'),
    ('김연아', '태영상선'),
    ('김희원', '㈜기가레인'),
]:
    cur.execute('''DELETE FROM candidates 
                   WHERE name_kr=? AND length(raw_text) < 500''', (name,))
    cur.execute('''UPDATE candidates SET is_duplicate=0
                   WHERE name_kr=? AND current_company=?''', (name, keep_company))

# 3. 권효상 — 깡통 삭제, dup:1 베스핀글로벌 삭제
cur.execute('DELETE FROM candidates WHERE id LIKE "32e22567%" AND name_kr="권효상"')
cur.execute('DELETE FROM candidates WHERE id LIKE "9d1f2bab%"')

# 4. 김신애 — current_company 정정
cur.execute('''UPDATE candidates SET current_company=NULL
               WHERE name_kr="김신애" AND current_company="<성격의 장·단점>"''')

conn.commit()
conn.close()
print("클렌징 완료")
