import os, sys, sqlite3, json
from neo4j import GraphDatabase
sys.stdout.reconfigure(encoding='utf-8')

def check_candidate():
    target_id = 'f5875fc2-99aa-4605-9742-5ec93f4cd51a'
    
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
    conn.close()

    # 2. Check Neo4j
    uri = os.environ.get('NEO4J_URI', 'bolt://127.0.0.1:7687')
    user = os.environ.get('NEO4J_USERNAME', 'neo4j')
    password = os.environ.get('NEO4J_PASSWORD', 'toss1234')
    try:
        driver = GraphDatabase.driver(uri, auth=(user, password))
        with driver.session() as session:
            res = session.run('MATCH (c:Candidate {id: $id}) RETURN c.id, c.name_kr', id=target_id)
            print(f"Neo4j Found: {res.single()}")
            
            print("Neo4j Skills:")
            res_s = session.run('MATCH (c:Candidate {id: $id})-[r]->(s:Skill) RETURN s.name, type(r)', id=target_id)
            for r in res_s:
                print(f"  - {r[0]} ({r[1]})")
        driver.close()
    except Exception as e:
        print(f"Neo4j Error: {e}")

if __name__ == "__main__":
    check_candidate()
