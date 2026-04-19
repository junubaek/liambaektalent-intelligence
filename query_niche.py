import sqlite3

query = """
SELECT '프롬프트엔지니어' as type, count(*) 
FROM candidates 
WHERE raw_text LIKE '%프롬프트%' OR raw_text LIKE '%Prompt%'
UNION ALL
SELECT 'LLM엔지니어', count(*) 
FROM candidates 
WHERE raw_text LIKE '%LLM%' OR raw_text LIKE '%거대언어모델%'
UNION ALL
SELECT 'DataPM', count(*) 
FROM candidates 
WHERE raw_text LIKE '%Data PM%' OR raw_text LIKE '%데이터 PM%'
UNION ALL
SELECT 'TechRecruiter', count(*) 
FROM candidates 
WHERE raw_text LIKE '%테크 리크루터%' OR raw_text LIKE '%개발자 채용%' OR raw_text LIKE '%IT 채용%'
UNION ALL
SELECT 'Flutter', count(*) 
FROM candidates 
WHERE raw_text LIKE '%Flutter%' OR raw_text LIKE '%플러터%'
"""

conn = sqlite3.connect('candidates.db')
cursor = conn.cursor()
cursor.execute(query)
rows = cursor.fetchall()
for r in rows:
    print(f'{r[0]}: {r[1]}명')
