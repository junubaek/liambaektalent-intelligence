import json, sqlite3, sys
sys.stdout.reconfigure(encoding='utf-8')
from neo4j import GraphDatabase

secrets = json.load(open('secrets.json'))
driver = GraphDatabase.driver(secrets['NEO4J_URI'], auth=(secrets['NEO4J_USERNAME'], secrets['NEO4J_PASSWORD']))
session = driver.session()

cid = 'c3d4ee55-266a-44f6-8e66-fb7486be38a8'

res = session.run('''
    MATCH (c:Candidate {id: $cid})
    RETURN c.name_kr as name, c.summary as summary, c.current_company as current_company, c.sector as sector
''', cid=cid).single()

print(f'이름: {res["name"]}')
print(f'current_company: {res["current_company"]}')
print(f'sector: {res["sector"]}')
print(f'summary: {res["summary"]}')
driver.close()

# SQLite raw_text 앞 300자
conn = sqlite3.connect('candidates.db')
cur = conn.cursor()
cur.execute('SELECT profile_summary, raw_text FROM candidates WHERE id = ?', (cid,))
row = cur.fetchone()
print()
print(f'SQLite profile_summary: {row[0]}')
print(f'SQLite raw_text 앞 300자: {row[1][:300] if row[1] else "없음"}')
conn.close()
