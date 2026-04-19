import sqlite3
import re
from neo4j import GraphDatabase

conn = sqlite3.connect('C:/Users/cazam/Downloads/이력서자동분석검색시스템/candidates.db')
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

# Get neo4j ids vs candidate ids if necessary
driver = GraphDatabase.driver('neo4j://127.0.0.1:7687', auth=('neo4j', 'toss1234'))
with driver.session() as s:
    neo_ids = [r['id'] for r in s.run('MATCH (c:Candidate) RETURN c.id as id').data()]

# Fetch based on candidate.id or document_hash
cursor.execute('SELECT id, document_hash, raw_text FROM candidates')
matches = []
patterns = [r'kong\b', r'api\s*gateway', r'kong\s*g/w', r'kong\s*api', r'트래픽\s*관리', r'라우팅', r'routing']

for row in cursor.fetchall():
    text = str(row['raw_text'] or '').lower()
    if not text: continue
    if any(re.search(p, text) for p in patterns):
        cid = row['id']
        chash = row['document_hash']
        if cid in neo_ids:
            matches.append(cid)
        elif chash in neo_ids:
            matches.append(chash)

print(f"Candidates with API_Gateway keywords matched to Neo4j IDs: {len(matches)}")

with driver.session() as session:
    session.run("MERGE (s:Skill {name: 'API_Gateway'})")
    cypher = '''
    MATCH (c:Candidate)
    WHERE c.id IN $hashes
    MERGE (s:Skill {name: 'API_Gateway'})
    MERGE (c)-[:BUILT]->(s)
    RETURN count(c) as cnt
    '''
    res = session.run(cypher, hashes=matches)
    print(f"Graph nodes updated: {res.single()['cnt']}")
driver.close()
