import sqlite3
import json
import sys
sys.stdout.reconfigure(encoding='utf-8')
from neo4j import GraphDatabase

# 1. Get Active IDs from SQLite
con = sqlite3.connect('candidates.db')
c = con.cursor()
c.execute("SELECT id FROM candidates WHERE is_duplicate=0")
active_ids = [r[0] for r in c.fetchall()]

# 2. Connect to Neo4j
try:
    with open('secrets.json', 'r', encoding='utf-8') as f:
        secrets = json.load(f)
    driver = GraphDatabase.driver('bolt://localhost:7687', auth=('neo4j', secrets.get('NEO4J_PASSWORD', 'toss1234')))
except Exception as e:
    print('Failed to connect to Neo4j', e)
    sys.exit(1)

with driver.session() as session:
    # 3. Identify Ghost Nodes
    query = '''
    MATCH (c:Candidate)
    WHERE NOT c.id IN $active_ids
    RETURN c.id AS id, c.name_kr AS name, COUNT { (c)-->() } AS edge_count
    ORDER BY edge_count DESC
    '''
    result = session.run(query, active_ids=active_ids)
    
    ghosts = []
    for record in result:
        ghosts.append({
            'id': record['id'],
            'name': record['name'],
            'edge_count': record['edge_count']
        })
        
    high_edge_ghosts = [g for g in ghosts if g['edge_count'] >= 10]
    low_edge_ghosts = [g for g in ghosts if g['edge_count'] < 10]
    
    print(f'Total Ghosts Found: {len(ghosts)}')
    print(f'- High Edge Ghosts (>=10): {len(high_edge_ghosts)}')
    print(f'- Low Edge Ghosts (<10): {len(low_edge_ghosts)}')
    
    if high_edge_ghosts:
        print('\n--- High Edge Ghosts (Requires Review) ---')
        for g in high_edge_ghosts[:20]:
            print(f"ID: {g['id']} => Name: {g['name']} => Edges: {g['edge_count']}")
            
    if low_edge_ghosts:
        print('\n--- Deleting Low Edge Ghosts ---')
        low_ids = [g['id'] for g in low_edge_ghosts]
        del_query = '''
        MATCH (c:Candidate)
        WHERE c.id IN $low_ids
        DETACH DELETE c
        '''
        session.run(del_query, low_ids=low_ids)
        print(f'{len(low_ids)} low-edge ghosts deleted.')
        
    # 4. Final Count
    final_count = session.run('MATCH (n:Candidate) RETURN count(n) AS cnt').single()['cnt']
    print(f'\nFinal Candidate Nodes in Neo4j: {final_count} (Target: {len(active_ids)})')
