import sqlite3, json, sys
sys.stdout.reconfigure(encoding='utf-8')
from neo4j import GraphDatabase

conn = sqlite3.connect('candidates.db')
cur = conn.cursor()
cur.execute('''SELECT id, name_kr, current_company, profile_summary, 
               length(raw_text) as rt_len
               FROM candidates WHERE name_kr = '이상헌' AND is_duplicate = 0''')
row = cur.fetchone()
if row:
    print(f'ID: {row[0]}')
    print(f'name_kr: {row[1]}')
    print(f'current_company: {row[2]}')
    print(f'profile_summary: {row[3]}')
    print(f'raw_text 길이: {row[4]}')

    cur.execute("SELECT raw_text FROM candidates WHERE id = ?", (row[0],))
    raw_fetch = cur.fetchone()
    raw = raw_fetch[0] if raw_fetch else None
    print(f'raw_text 앞 500자:')
    print(raw[:500] if raw else '없음')
else:
    print("이상헌(is_duplicate=0)을 찾을 수 없습니다.")
    # 검색을 위해 중복 제거 없이도 확인
    cur.execute("SELECT id, name_kr, current_company, is_duplicate FROM candidates WHERE name_kr = '이상헌'")
    others = cur.fetchall()
    if others:
        print(f"중복 처리된 항목이 {len(others)}개 발견되었습니다:")
        for o in others:
            print(f" - ID: {o[0]}, 회사: {o[2]}, 중복여부: {o[3]}")
conn.close()

if row:
    try:
        secrets = json.load(open('secrets.json'))
        driver = GraphDatabase.driver(secrets['NEO4J_URI'], auth=(secrets['NEO4J_USERNAME'], secrets['NEO4J_PASSWORD']))
        with driver.session() as session:
            skills = session.run('MATCH (c:Candidate {id: $cid})-[r]->(s:Skill) RETURN s.name, type(r)', cid=row[0]).data()
            print(f'\nNeo4j 스킬: {len(skills)}개')
            for s in skills[:10]:
                print(f'  {s["s.name"]} ({s["type(r)"]})')
        driver.close()
    except Exception as e:
        print(f"\nNeo4j 연결 또는 쿼리 중 오류 발생: {e}")
