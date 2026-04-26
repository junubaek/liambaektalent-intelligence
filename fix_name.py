import sqlite3
from neo4j import GraphDatabase

target_id = '32022567-1b6f-81cf-af18-cbdada2eecf0'
real_name = '이정윤'

# 1. Update SQLite
db_path = 'candidates.db'
conn = sqlite3.connect(db_path)
cur = conn.cursor()
cur.execute("UPDATE candidates SET name_kr = ?, is_neo4j_synced = 0 WHERE id = ?", (real_name, target_id))
conn.commit()
conn.close()
print(f"Updated SQLite for ID {target_id} to name_kr = {real_name}")

# 2. Update AuraDB
uri = 'neo4j+ssc://72de4959.databases.neo4j.io'
driver = GraphDatabase.driver(uri, auth=('72de4959', 'oicDGhFqhTz-5NhnnW0uGEKOIrSUs0GZBdKtzRhyvns'))
try:
    with driver.session() as s:
        res = s.run("""
        MATCH (c:Candidate {id: $id})
        SET c.name_kr = $name, c.name = $name
        RETURN c.id, c.name_kr
        """, id=target_id, name=real_name).single()
        if res:
            print(f"Updated AuraDB for Candidate: {res['c.name_kr']}")
        else:
            print("Candidate not found in AuraDB!?")
finally:
    driver.close()

# 3. Update Local Neo4j (if running)
try:
    local_driver = GraphDatabase.driver("bolt://127.0.0.1:7687", auth=("neo4j", "toss1234"))
    with local_driver.session() as s:
        s.run("""
        MATCH (c:Candidate {id: $id})
        SET c.name_kr = $name, c.name = $name
        """, id=target_id, name=real_name)
    local_driver.close()
    print("Updated Local Neo4j as well.")
except Exception as e:
    print("Local Neo4j update failed (maybe offline):", e)
