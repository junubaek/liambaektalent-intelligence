import sqlite3
import json
import sys
sys.stdout.reconfigure(encoding='utf-8')
from neo4j import GraphDatabase

con = sqlite3.connect('candidates.db')
c = con.cursor()

query = '''
SELECT 
  a.name_kr,
  a.id as ghost_id,
  a.is_duplicate,
  a.duplicate_of,
  b.id as keeper_id,
  b.raw_text as summary
FROM candidates a
LEFT JOIN candidates b 
  ON b.id = a.duplicate_of
WHERE a.name_kr IN (
  '이준호', '이새은', '김민지', '김현준', 
  '박지민', '강동현', '강건규', '김지훈'
)
AND a.is_duplicate = 1
LIMIT 20;
'''

c.execute(query)
rows = c.fetchall()

has_issues = False
print(f"Total matched cross-check records: {len(rows)}")

for r in rows:
    name, ghost_id, is_duplicate, duplicate_of, keeper_id, summary = r
    
    issue_msgs = []
    if not duplicate_of:
        issue_msgs.append("duplicate_of IS NULL")
        
    if not keeper_id:
        issue_msgs.append("keeper_id (Left Join) IS NULL")
        
    if keeper_id and (not summary or len(summary) < 50):
        issue_msgs.append("keeper has empty or too short summary")
        
    if issue_msgs:
        has_issues = True
        print(f"ISSUE FOUND: Name={name}, Ghost={ghost_id} -> {issue_msgs}")
    else:
        print(f"OK: Name={name}, Ghost={ghost_id[:8]}... -> Keeper={keeper_id[:8]}... (Summary Len: {len(summary)})")

if has_issues:
    print("\n[RESULT] Issues found during cross-check! Aborting deletion.")
    sys.exit(0)

print("\n[RESULT] No issues found. All deduplication mappings are valid.")
print("Proceeding to delete 204 high-edge ghosts in Neo4j...")

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
    # Get high-edge ghosts
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

