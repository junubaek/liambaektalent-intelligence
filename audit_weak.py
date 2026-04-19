import sqlite3
import pandas as pd

db_path = 'C:/Users/cazam/Downloads/이력서자동분석검색시스템/candidates.db'
conn = sqlite3.connect(db_path)

q1 = """
SELECT 
  name_kr,
  length(raw_text) as text_len,
  raw_text
FROM candidates
WHERE length(raw_text) < 200
ORDER BY text_len DESC
LIMIT 20
"""

q2 = """
SELECT 
  CASE 
    WHEN length(raw_text) = 0 THEN '0자'
    WHEN length(raw_text) < 50 THEN '1-49자'
    WHEN length(raw_text) < 100 THEN '50-99자'
    WHEN length(raw_text) < 150 THEN '100-149자'
    ELSE '150-199자'
  END as 구간,
  COUNT(*) as 수
FROM candidates
WHERE length(raw_text) < 200
GROUP BY 1
ORDER BY 2 DESC
"""

print('=== 1. 상위 20명 샘플 (길이 역순) ===')
df1 = pd.read_sql_query(q1, conn)
for i, row in df1.iterrows():
    rt = row['raw_text'].replace('\\n', ' ')
    print(f"{row['name_kr']} ({row['text_len']}자): {rt}")

print('\\n=== 2. 구간별 분포 ===')
df2 = pd.read_sql_query(q2, conn)
for i, row in df2.iterrows():
    print(f"{row['구간']}: {row['수']}명")
