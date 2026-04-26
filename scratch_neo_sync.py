import sqlite3, json, sys, os
sys.stdout.reconfigure(encoding='utf-8')
from neo4j import GraphDatabase

with open("secrets.json", "r", encoding="utf-8") as f:
    secrets = json.load(f)

uri = secrets.get('NEO4J_URI', 'neo4j+s://72de4959.databases.neo4j.io')
user = secrets.get('NEO4J_USERNAME', 'neo4j')
pw = secrets.get('NEO4J_PASSWORD')

driver = GraphDatabase.driver(uri, auth=(user, pw))

conn = sqlite3.connect('candidates.db')
conn.row_factory = sqlite3.Row
cur = conn.cursor()

# 재파싱 후 Neo4j 업데이트 필요한 후보자
cur.execute('''
    SELECT id, name_kr, profile_summary, sector, total_years
    FROM candidates
    WHERE is_duplicate=0
    AND is_neo4j_synced=1
    AND profile_summary IS NOT NULL
    AND profile_summary != ''
    ORDER BY ROWID DESC
    LIMIT 200
''')
rows = cur.fetchall()
print(f'Neo4j 업데이트 대상: {len(rows)}명')

updated = 0
with driver.session() as s:
    for r in rows:
        s.run('''
            MATCH (c:Candidate {id: $id})
            SET c.sector = $sector,
                c.profile_summary = $summary,
                c.total_years = $total_years
        ''', id=r['id'], sector=r['sector'] or '', summary=r['profile_summary'], total_years=r['total_years'])
        updated += 1
        if updated % 50 == 0:
            print(f'  {updated}/{len(rows)} 완료')

print(f'Neo4j 업데이트 완료: {updated}명')
driver.close()
conn.close()
