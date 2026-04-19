import sqlite3
import re

db_path = 'C:/Users/cazam/Downloads/이력서자동분석검색시스템/candidates.db'
conn = sqlite3.connect(db_path)
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

print('=== 1. candidates 테이블 스키마 ===')
cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='candidates'")
schema_c = cursor.fetchone()
print(schema_c['sql'] if schema_c else 'Table not found')

print('\\n=== 2. raw_text 출생연도/학력 패턴 확인 (LIMIT 5) ===')
cursor.execute("SELECT id, name_kr, raw_text FROM candidates LIMIT 5")
rows = cursor.fetchall()
for row in rows:
    rt = row['raw_text'] or ''
    # Find birth year like 19xx, 20xx
    birth_matches = re.findall(r'(19[5-9]\\d|20[0-2]\\d)[^0-9]?년?생?|[^\\w](19[5-9]\\d|20[0-2]\\d)\\.', rt)
    # Find education keywords
    edu_matches = re.findall(r'대학교|학사|석사|박사|졸업|고등학교', rt)
    
    print(f'Candidate: {row["name_kr"]}')
    print(f'  Birth Year hints: {list(set([m[0] or m[1] for m in birth_matches]))[:5]}')
    print(f'  Education hints: {list(set(edu_matches))[:5]}')

print('\\n=== 3. parsing_cache 테이블 스키마 ===')
cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='parsing_cache'")
schema_p = cursor.fetchone()
print(schema_p['sql'] if schema_p else 'Table not found')

print('\\n=== 3-1. parsed_json 데이터 샘플 (LIMIT 2) ===')
cursor.execute("SELECT parsed_json FROM parsing_cache LIMIT 2")
p_rows = cursor.fetchall()
for r in p_rows:
    print(r['parsed_json'][:300], '...')
