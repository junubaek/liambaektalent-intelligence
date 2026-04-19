import sqlite3
import json
import sys
sys.stdout.reconfigure(encoding='utf-8')
from neo4j import GraphDatabase

con = sqlite3.connect('candidates.db')
c = con.cursor()
c.execute("SELECT id FROM candidates WHERE is_duplicate=0")
active_ids = [r[0] for r in c.fetchall()]

try:
    with open('secrets.json', 'r', encoding='utf-8') as f:
        secrets = json.load(f)
    driver = GraphDatabase.driver('bolt://localhost:7687', auth=('neo4j', secrets.get('NEO4J_PASSWORD', 'toss1234')))
except Exception as e:
    print('Failed to connect to Neo4j', e)
    sys.exit(1)

with driver.session() as session:
    q = '''
    MATCH (c:Candidate)
    WHERE NOT c.id IN $active_ids
    WITH c, COUNT { (c)-->() } AS edge_count
    WHERE edge_count >= 10
    RETURN c.id AS id
    '''
    res = session.run(q, active_ids=active_ids)
    high_ids = [record['id'] for record in res]
    
    if high_ids:
        del_q = '''
        MATCH (c:Candidate)
        WHERE c.id IN $high_ids
        DETACH DELETE c
        '''
        session.run(del_q, high_ids=high_ids)
        print(f"Successfully deleted {len(high_ids)} high-edge ghost nodes from Neo4j.")
    
    # Final Count
    final_count = session.run('MATCH (n:Candidate) RETURN count(n) AS cnt').single()['cnt']
    print(f'Final Candidate Nodes in Neo4j: {final_count} (Target: {len(active_ids)})')
