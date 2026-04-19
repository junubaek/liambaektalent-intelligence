import sqlite3
import pandas as pd

conn = sqlite3.connect('candidates.db')
query = """
SELECT '반도체' as type, count(*) FROM candidates WHERE raw_text LIKE '%반도체%' OR raw_text LIKE '%semiconductor%'
UNION ALL
SELECT '자동차SW', count(*) FROM candidates WHERE raw_text LIKE '%AUTOSAR%' OR raw_text LIKE '%자동차%' AND raw_text LIKE '%개발%'
UNION ALL
SELECT '배터리', count(*) FROM candidates WHERE raw_text LIKE '%배터리%' OR raw_text LIKE '%Battery%'
UNION ALL
SELECT '사내변호사', count(*) FROM candidates WHERE raw_text LIKE '%변호사%' OR raw_text LIKE '%법무법인%'
UNION ALL
SELECT '특허', count(*) FROM candidates WHERE raw_text LIKE '%특허%' OR raw_text LIKE '%patent%'
UNION ALL
SELECT '애널리스트', count(*) FROM candidates WHERE raw_text LIKE '%애널리스트%' OR raw_text LIKE '%analyst%' AND raw_text LIKE '%증권%'
UNION ALL
SELECT '펀드매니저', count(*) FROM candidates WHERE raw_text LIKE '%펀드%' OR raw_text LIKE '%자산운용%'
UNION ALL
SELECT '영상PD', count(*) FROM candidates WHERE raw_text LIKE '%PD%' OR raw_text LIKE '%연출%' OR raw_text LIKE '%영상 제작%'
UNION ALL
SELECT '임상CRA', count(*) FROM candidates WHERE raw_text LIKE '%임상%' OR raw_text LIKE '%CRA%' OR raw_text LIKE '%CRO%'
UNION ALL
SELECT '패션MD', count(*) FROM candidates WHERE raw_text LIKE '%패션%' AND raw_text LIKE '%MD%'
UNION ALL
SELECT '일본어사업', count(*) FROM candidates WHERE raw_text LIKE '%일본%' AND raw_text LIKE '%사업%'
UNION ALL
SELECT '동남아', count(*) FROM candidates WHERE raw_text LIKE '%동남아%' OR raw_text LIKE '%베트남%' OR raw_text LIKE '%인도네시아%'
UNION ALL
SELECT '에듀테크', count(*) FROM candidates WHERE raw_text LIKE '%에듀테크%' OR raw_text LIKE '%교육%' AND raw_text LIKE '%플랫폼%'
UNION ALL
SELECT '로봇', count(*) FROM candidates WHERE raw_text LIKE '%로봇%' OR raw_text LIKE '%Robot%'
UNION ALL
SELECT 'AI반도체', count(*) FROM candidates WHERE raw_text LIKE '%NPU%' OR raw_text LIKE '%AI 반도체%' OR raw_text LIKE '%AI칩%'
"""

try:
    df = pd.read_sql_query(query, conn)
    print(df.to_markdown(index=False))
except Exception as e:
    cursor = conn.cursor()
    cursor.execute(query)
    results = cursor.fetchall()
    for row in results:
        print(f"{row[0]} | {row[1]}")
conn.close()
