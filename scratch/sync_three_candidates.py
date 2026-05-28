import sqlite3
import sys
import json
from neo4j import GraphDatabase

conn = sqlite3.connect('candidates.db')
cur = conn.cursor()

names = ['김국현', '우형일', '황의영']
for name in names:
    cur.execute('''SELECT id, name_kr, sector, profile_summary, current_company
                   FROM candidates WHERE name_kr=? AND is_duplicate=0''', (name,))
    row = cur.fetchone()
    if row:
        print(f'{name}: id={row[0][:8]}... sector={row[2]} company={row[4]}')

secrets = json.load(open('secrets.json', encoding='utf-8'))
driver = GraphDatabase.driver(secrets['NEO4J_URI'],
         auth=(secrets['NEO4J_USERNAME'], secrets['NEO4J_PASSWORD']))
session = driver.session()

for name in names:
    cur.execute('SELECT id, sector, profile_summary, current_company FROM candidates WHERE name_kr=? AND is_duplicate=0', (name,))
    row = cur.fetchone()
    if not row: continue
    cid, sector, summary, company = row
    
    # Aura에서 현재 값 확인
    result = session.run('MATCH (c:Candidate {id: $id}) RETURN c.sector, c.summary, c.current_company', id=cid).single()
    if result:
        print(f'Aura [{name}]: sector={result[0]} company={result[2]}')
    else:
        print(f'Aura [{name}]: 노드 없음')
    
    # 업데이트
    session.run('''MATCH (c:Candidate {id: $id})
                   SET c.sector=$sector, c.summary=$summary, c.current_company=$company''',
                id=cid, sector=sector, summary=summary, company=company)
    print(f'  → 업데이트 완료')

conn.close()
driver.close()
