import sqlite3, json, sys
sys.stdout.reconfigure(encoding='utf-8')
from neo4j import GraphDatabase

conn = sqlite3.connect('candidates.db')
cur = conn.cursor()
cur.execute('SELECT id FROM candidates')
sqlite_ids = set(r[0] for r in cur.fetchall())
conn.close()

secrets = json.load(open('secrets.json', encoding='utf-8'))
driver = GraphDatabase.driver(secrets['NEO4J_URI'], auth=(secrets['NEO4J_USERNAME'], secrets['NEO4J_PASSWORD']))
session = driver.session()

neo4j_ids = set(r['id'] for r in session.run('MATCH (c:Candidate) RETURN c.id as id').data())
only_neo4j = neo4j_ids - sqlite_ids

# 샘플 50개 상세 확인
result = session.run('''
    MATCH (c:Candidate)
    WHERE c.id IN $ids
    RETURN c.id as id, c.name_kr as name_kr, c.current_company as current_company, c.sector as sector,
           COUNT { (c)-[:MANAGED|BUILT|DESIGNED|ANALYZED|LED]->(:Skill) } as skill_cnt
    ORDER BY skill_cnt DESC
    LIMIT 50
''', ids=list(only_neo4j)[:200]).data()

valid = [r for r in result if r['name_kr'] and len(r['name_kr']) >= 2 and r['name_kr'] not in ['원본','재무회계','UX컨설팅']]
print(f'Neo4j 전용 노드: {len(only_neo4j)}개')
print(f'샘플 50개 중 유효: {len(valid)}개\n')

for r in valid[:20]:
    print(f'  {r["name_kr"]:10s} | {r["current_company"]} | 스킬:{r["skill_cnt"]}개')

driver.close()
