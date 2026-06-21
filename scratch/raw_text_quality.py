import sqlite3, sys, os
sys.stdout.reconfigure(encoding='utf-8')
conn = sqlite3.connect(os.path.join(os.path.dirname(__file__), '..', 'candidates.db'))
cur = conn.cursor()

# raw_text 길이 분포
cur.execute("""
    SELECT 
        COUNT(CASE WHEN length(raw_text) < 100 THEN 1 END) as very_short,
        COUNT(CASE WHEN length(raw_text) BETWEEN 100 AND 500 THEN 1 END) as short,
        COUNT(CASE WHEN length(raw_text) BETWEEN 500 AND 2000 THEN 1 END) as medium,
        COUNT(CASE WHEN length(raw_text) > 2000 THEN 1 END) as good,
        COUNT(CASE WHEN raw_text IS NULL THEN 1 END) as null_count
    FROM candidates WHERE is_duplicate=0
""")
r = cur.fetchone()
print(f'100자 미만(파싱실패): {r[0]}명')
print(f'100-500자(빈약): {r[1]}명')
print(f'500-2000자(보통): {r[2]}명')
print(f'2000자 이상(양호): {r[3]}명')
print(f'NULL: {r[4]}명')

conn.close()
