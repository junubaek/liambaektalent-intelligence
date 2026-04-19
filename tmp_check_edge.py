import json
from neo4j import GraphDatabase

uri = "neo4j://127.0.0.1:7687"
driver = GraphDatabase.driver(uri, auth=("neo4j", "toss1234"))

cypher = """
MATCH (c:Candidate)-[r]->(s:Skill)
WHERE c.name CONTAINS '이가영'
RETURN type(r) AS rel, s.name AS skill, c.name AS name
ORDER BY type(r)
"""

with driver.session() as session:
    res = list(session.run(cypher))
if res:
    print("=== Neo4j Edges ===")
    for r in res:
        print(f"- {r['rel']} -> {r['skill']}")
else:
    print("No nodes found.")
driver.close()

with open("candidates_cache_jd.json", "r", encoding="utf-8") as f:
    cands = json.load(f)
for c in cands:
    if "이가영" in c["name"] and "문피아" in c["name"]:
        print("\n=== Resume Content ===")
        print(c["summary"])
