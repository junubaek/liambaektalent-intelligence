import sqlite3
import json
import sys
from neo4j import GraphDatabase

sys.stdout.reconfigure(encoding='utf-8')
con = sqlite3.connect('candidates.db')
c = con.cursor()
c.execute("SELECT id FROM candidates WHERE is_duplicate=0")
active_ids = {r[0] for r in c.fetchall()}

with open('secrets.json', 'r', encoding='utf-8') as f:
    secrets = json.load(f)
driver = GraphDatabase.driver('bolt://localhost:7687', auth=('neo4j', secrets.get('NEO4J_PASSWORD', 'toss1234')))

with driver.session() as session:
    res = session.run("MATCH (c:Candidate) RETURN c.id as id")
    neo4j_ids = {r['id'] for r in res}

ghosts = neo4j_ids - active_ids
print(f'Active IDs: {len(active_ids)}')
print(f'Neo4j IDs: {len(neo4j_ids)}')
print(f'Ghosts: {len(ghosts)}')

if len(ghosts) > 0:
    q = '''
    MATCH (c:Candidate) WHERE c.id IN $ghosts
    DETACH DELETE c
    '''
    with driver.session() as session:
        session.run(q, ghosts=list(ghosts))
    print("Deleted remaining ghost nodes.")
    
    count = driver.session().run("MATCH (c:Candidate) RETURN count(c) as cnt").single()['cnt']
    print("Final Node Count:", count)
