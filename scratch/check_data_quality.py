import sqlite3, sys
sys.stdout.reconfigure(encoding='utf-8')
conn = sqlite3.connect('candidates.db')
cur = conn.cursor()

cur.execute('SELECT COUNT(*) FROM candidates WHERE is_duplicate=0')
total = cur.fetchone()[0]
print(f'전체 마스터: {total}명')

# 1. 깡통 마스터 (raw_text 없음)
cur.execute('SELECT COUNT(*) FROM candidates WHERE is_duplicate=0 AND (raw_text IS NULL OR length(raw_text) < 10)')
print(f'깡통 마스터 (raw_text 없음): {cur.fetchone()[0]}명')

# 2. 파편 마스터 (raw_text 500자 미만)
cur.execute('SELECT COUNT(*) FROM candidates WHERE is_duplicate=0 AND length(raw_text) BETWEEN 10 AND 500')
print(f'파편 마스터 (500자 미만): {cur.fetchone()[0]}명')

# 3. current_company 파싱 오류 의심
cur.execute('''SELECT COUNT(*) FROM candidates WHERE is_duplicate=0 
               AND current_company IS NOT NULL
               AND (current_company LIKE "<%>" OR length(current_company) > 50)''')
print(f'current_company 파싱 오류 의심: {cur.fetchone()[0]}명')

# 4. 마스터가 2개 이상인 이름
cur.execute('''SELECT COUNT(*) FROM (
    SELECT name_kr FROM candidates WHERE is_duplicate=0
    GROUP BY name_kr HAVING COUNT(*) > 1
)''')
print(f'마스터 2개 이상 이름: {cur.fetchone()[0]}건')

# 5. 깡통인데 진짜 데이터가 dup:1에 있는 케이스
cur.execute('''SELECT COUNT(DISTINCT d.name_kr) FROM candidates d
               JOIN candidates m ON d.name_kr = m.name_kr
               WHERE m.is_duplicate=0 AND length(m.raw_text) < 10
               AND d.is_duplicate=1 AND length(d.raw_text) > 500''')
print(f'깡통 마스터 + 진짜 dup:1 케이스: {cur.fetchone()[0]}명')

conn.close()
