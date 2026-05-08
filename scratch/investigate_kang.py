import sqlite3, json, sys
sys.stdout.reconfigure(encoding='utf-8')
from neo4j import GraphDatabase

conn = sqlite3.connect('candidates.db')
cur = conn.cursor()
cur.execute('SELECT id, name_kr, current_company, sector, profile_summary, raw_text FROM candidates WHERE name_kr = "강기태" AND is_duplicate = 0')
row = cur.fetchone()
if not row:
    print("Candidate Kang Ki-tae not found.")
    sys.exit(0)

cid, name, company, sector, summary, raw_text = row
print(f"Name: {name} | Company: {company} | Sector: {sector}")
print(f"Summary: {summary}")
print(f"Raw Text Sample: {raw_text[:500]}...")
conn.close()

secrets = json.load(open('secrets.json'))
driver = GraphDatabase.driver(secrets['NEO4J_URI'], auth=(secrets['NEO4J_USERNAME'], secrets['NEO4J_PASSWORD']))
with driver.session() as session:
    res = session.run('''
        MATCH (c:Candidate {id: $cid})-[r]->(t)
        RETURN type(r) as rel_type, labels(t) as target_labels, t.name as target_name, t.id as target_id
    ''', cid=cid)
    print("\n[Neo4j Edges]")
    for r in res:
        label = r["target_labels"][0] if r["target_labels"] else "None"
        print(f" - {r['rel_type']} -> [{label}] {r['target_name']} ({r['target_id']})")
driver.close()
