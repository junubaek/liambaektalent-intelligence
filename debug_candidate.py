import os, sys, sqlite3, json
from neo4j import GraphDatabase

sys.stdout.reconfigure(encoding='utf-8')

def check_candidate(target_id):
    # 1. Check SQLite
    conn = sqlite3.connect('candidates.db')
    cur = conn.cursor()
    cur.execute('SELECT name_kr, current_company, total_years, careers_json FROM candidates WHERE id = ?', (target_id,))
    row = cur.fetchone()
    if row:
        print(f"SQLite Found: {row[0]} ({row[1]}) {row[2]}yrs")
        careers = json.loads(row[3] or '[]')
        print("Careers:")
        for job in careers:
            print(f"  - {job.get('company')} | {job.get('position')} | {job.get('period')}")
    else:
        print(f"ID {target_id} not found in SQLite.")
    conn.close()

    # 2. Check Neo4j (Remote)
    with open("secrets.json", "r") as f:
        secrets = json.load(f)
    uri = secrets.get('NEO4J_URI')
    user = secrets.get('NEO4J_USERNAME')
    password = secrets.get('NEO4J_PASSWORD')
    
    try:
        driver = GraphDatabase.driver(uri, auth=(user, password))
        with driver.session() as session:
            res = session.run('MATCH (c:Candidate {id: $id}) RETURN c.id, c.name_kr', id=target_id)
            node = res.single()
            if node:
                print(f"Neo4j Found: ID={node['c.id']}, Name={node['c.name_kr']}")
                print("Neo4j Skills:")
                res_s = session.run('MATCH (c:Candidate {id: $id})-[r]->(s:Skill) RETURN s.name, type(r)', id=target_id)
                for r in res_s:
                    print(f"  - {r[0]} ({r[1]})")
            else:
                print(f"ID {target_id} not found in Neo4j.")
        driver.close()
    except Exception as e:
        print(f"Neo4j Error: {e}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        check_candidate(sys.argv[1])
    else:
        print("Usage: python debug_candidate.py <ID>")
