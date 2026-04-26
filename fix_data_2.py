import sqlite3
from neo4j import GraphDatabase

kim_id = '31f22567-1b6f-81ed-a55b-c13430ebacfd'
kim_new_phone = '010-7240-8266'

seo_id = '32e22567-1b6f-81fe-8eef-d7e7307618e1'
seo_new_name = '장주호'

print("1. Updating SQLite")
conn = sqlite3.connect('candidates.db')
cur = conn.cursor()

# Fix Kim
cur.execute("UPDATE candidates SET phone = ? WHERE id = ?", (kim_new_phone, kim_id))
# Fix Seo
cur.execute("UPDATE candidates SET name_kr = ? WHERE id = ?", (seo_new_name, seo_id))

conn.commit()
conn.close()
print("SQLite Updated.")

print("2. Updating AuraDB")
uri = 'neo4j+ssc://72de4959.databases.neo4j.io'
driver = GraphDatabase.driver(uri, auth=('72de4959', 'oicDGhFqhTz-5NhnnW0uGEKOIrSUs0GZBdKtzRhyvns'))
try:
    with driver.session() as s:
        # Update Name only for Seo
        s.run("MATCH (c:Candidate {id: $id}) SET c.name_kr = $name, c.name = $name", id=seo_id, name=seo_new_name)
    print("AuraDB Updated.")
finally:
    driver.close()

print("3. Updating Local Neo4j")
try:
    local_driver = GraphDatabase.driver("bolt://127.0.0.1:7687", auth=("neo4j", "toss1234"))
    with local_driver.session() as s:
        s.run("MATCH (c:Candidate {id: $id}) SET c.name_kr = $name, c.name = $name", id=seo_id, name=seo_new_name)
    local_driver.close()
    print("Local Neo4j Updated.")
except Exception as e:
    print("Local Neo4j offline:", e)

print("Done completely.")
