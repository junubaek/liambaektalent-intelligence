import sqlite3, json, sys
from neo4j import GraphDatabase

sys.stdout.reconfigure(encoding='utf-8')

def run():
    with open('resync_missing_neo4j.json', 'r') as f:
        missing_ids = json.load(f)
    
    if not missing_ids:
        print("No missing IDs to process.")
        return

    print(f"Force creating {len(missing_ids)} nodes in Neo4j...")

    conn = sqlite3.connect('candidates.db')
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    placeholders = ','.join(['?'] * len(missing_ids))
    cur.execute(f"SELECT id, name_kr, current_company, sector, profile_summary FROM candidates WHERE id IN ({placeholders})", missing_ids)
    rows = cur.fetchall()
    conn.close()

    secrets = json.load(open('secrets.json'))
    driver = GraphDatabase.driver(secrets['NEO4J_URI'], auth=(secrets['NEO4J_USERNAME'], secrets['NEO4J_PASSWORD']))

    with driver.session() as session:
        for i, row in enumerate(rows):
            session.run("""
                MERGE (c:Candidate {id: $id})
                SET c.name_kr = $name,
                    c.current_company = $company,
                    c.sector = $sector,
                    c.summary = $summary
            """, id=row['id'], name=row['name_kr'], company=row['current_company'] or "", 
                 sector=row['sector'] or "미분류", summary=row['profile_summary'] or "")
            
            if (i+1) % 50 == 0:
                print(f"  Progress: {i+1}/{len(rows)}")

    driver.close()
    print("Force creation complete.")

if __name__ == '__main__':
    run()
