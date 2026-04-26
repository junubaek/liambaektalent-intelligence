import json, sqlite3, sys
from neo4j import GraphDatabase

def trace_origin():
    with open('secrets.json', 'r', encoding='utf-8') as f:
        secrets = json.load(f)
    driver = GraphDatabase.driver(secrets.get('NEO4J_URI'), auth=(secrets.get('NEO4J_USERNAME'), secrets.get('NEO4J_PASSWORD')))
    
    conn = sqlite3.connect('candidates.db')
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    with driver.session() as s:
        # 1. Dummy Samples (32/33)
        print('=== 1. Dummy Node Samples (ID STARTS WITH 32/33) ===')
        q_dummy = '''
        MATCH (c:Candidate)
        WHERE c.id STARTS WITH '32' OR c.id STARTS WITH '33'
        RETURN c.id as id, c.name_kr as name, size(c.id) as length
        LIMIT 10
        '''
        dummies = s.run(q_dummy).data()
        for d in dummies:
            cid = d['id']
            # Check in SQLite
            cur.execute('SELECT id, name_kr, phone FROM candidates WHERE id=?', (cid,))
            row = cur.fetchone()
            sqlite_status = "Exists in SQLite" if row else "Missing in SQLite"
            print(f"ID: {cid} ({d['length']}자) | Name: {d['name']} | SQLite: {sqlite_status}")

        # 2. Normal Samples
        print('\n=== 2. Normal Node Samples ===')
        q_normal = '''
        MATCH (c:Candidate)
        WHERE NOT (c.id STARTS WITH '32' OR c.id STARTS WITH '33')
        RETURN c.id as id, c.name_kr as name, size(c.id) as length
        LIMIT 5
        '''
        normals = s.run(q_normal).data()
        for n in normals:
            cid = n['id']
            # Check in SQLite
            cur.execute('SELECT id, name_kr, phone FROM candidates WHERE id=?', (cid,))
            row = cur.fetchone()
            sqlite_status = "Exists in SQLite" if row else "Missing in SQLite"
            print(f"ID: {cid} ({n['length']}자) | Name: {n['name']} | SQLite: {sqlite_status}")

    conn.close()
    driver.close()

if __name__ == "__main__":
    trace_origin()
