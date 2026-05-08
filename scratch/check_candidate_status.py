import sqlite3, json, sys
sys.stdout.reconfigure(encoding='utf-8')
from neo4j import GraphDatabase

conn = sqlite3.connect('candidates.db')
cur = conn.cursor()
secrets = json.load(open('secrets.json'))
driver = GraphDatabase.driver(secrets['NEO4J_URI'], auth=(secrets['NEO4J_USERNAME'], secrets['NEO4J_PASSWORD']))
session = driver.session()

for name in ['이상헌', '최우성', '정윤오']:
    cur.execute('SELECT id, name_kr, current_company, profile_summary, is_duplicate FROM candidates WHERE name_kr = ? AND is_duplicate = 0', (name,))
    row = cur.fetchone()
    if not row:
        print(f'[{name}] ❌ 마스터 없음')
        continue
    
    cid = row[0]
    # Fixed the escaping in the Cypher query
    skills = session.run('MATCH (c:Candidate {id: $cid})-[r]->(s:Skill) RETURN s.name as name, type(r) as type', cid=cid).data()
    
    print(f'[{name}]')
    print(f'  ID: {cid}')
    print(f'  현직: {row[2]}')
    print(f'  Neo4j 스킬: {len(skills)}개')
    for s in skills[:15]:
        print(f'    {s["name"]} ({s["type"]})')
    print()

session.close()
driver.close()
conn.close()
