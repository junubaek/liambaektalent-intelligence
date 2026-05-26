import sqlite3, json, sys
sys.stdout.reconfigure(encoding='utf-8')
from neo4j import GraphDatabase

# SQLite 현황
conn = sqlite3.connect('candidates.db')
cur = conn.cursor()

cur.execute('SELECT COUNT(*) FROM candidates')
total = cur.fetchone()[0]
cur.execute('SELECT COUNT(*) FROM candidates WHERE is_duplicate=0')
masters = cur.fetchone()[0]
cur.execute('SELECT COUNT(*) FROM candidates WHERE is_duplicate=1')
dups = cur.fetchone()[0]

# 동명이인 현황
cur.execute('''
    SELECT name_kr, COUNT(*) as cnt
    FROM candidates
    WHERE is_duplicate=0
    GROUP BY name_kr
    HAVING cnt > 1
    ORDER BY cnt DESC
    LIMIT 20
''')
multi_masters = cur.fetchall()

print(f'=== SQLite ===')
print(f'전체: {total}명')
print(f'마스터(is_duplicate=0): {masters}명')
print(f'중복(is_duplicate=1): {dups}명')
print(f'동명이인 마스터 중복: {len(multi_masters)}건')
for name, cnt in multi_masters[:10]:
    print(f'  {name}: {cnt}명')

conn.close()

# 로컬 Neo4j
secrets = json.load(open('secrets.json', encoding='utf-8'))
driver = GraphDatabase.driver(secrets['NEO4J_URI'], auth=(secrets['NEO4J_USERNAME'], secrets['NEO4J_PASSWORD']))
session = driver.session()

neo4j_total = session.run('MATCH (c:Candidate) RETURN count(c)').single()[0]
neo4j_with_skills = session.run('''
    MATCH (c:Candidate)
    WHERE (c)-[:MANAGED|BUILT|DESIGNED|ANALYZED|LED|LAUNCHED|GREW|NEGOTIATED]->(:Skill)
    RETURN count(c)
''').single()[0]

# SQLite에 없고 Neo4j에만 있는 것
sqlite_ids = set()
conn2 = sqlite3.connect('candidates.db')
cur2 = conn2.cursor()
cur2.execute('SELECT id FROM candidates WHERE is_duplicate=0')
for r in cur2.fetchall():
    sqlite_ids.add(r[0])
conn2.close()

neo4j_ids = set(r['id'] for r in session.run('MATCH (c:Candidate) RETURN c.id as id').data())
only_neo4j = neo4j_ids - sqlite_ids
only_sqlite = sqlite_ids - neo4j_ids

print(f'\n=== 로컬 Neo4j ===')
print(f'전체 노드: {neo4j_total}명')
print(f'스킬 있음: {neo4j_with_skills}명')
print(f'Neo4j에만 있음(SQLite 없음): {len(only_neo4j)}명')
print(f'SQLite에만 있음(Neo4j 없음): {len(only_sqlite)}명')

driver.close()
