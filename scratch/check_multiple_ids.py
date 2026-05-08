import json
from neo4j import GraphDatabase

with open("secrets.json", "r", encoding="utf-8") as f:
    secrets = json.load(f)

driver = GraphDatabase.driver(secrets["NEO4J_URI"], auth=(secrets["NEO4J_USERNAME"], secrets["NEO4J_PASSWORD"]))
ids = ['db752f0f-0f1a-437c-a09d-43c20442ab7b', '898ea4e0-77d4-46d5-bf4d-c2d5b4a04741', 'ba6d2583-fac1-474b-9df7-ee1b265ae34f', '55726c4a-4601-4ee9-87dc-581d15eda75e', '31f22567-1b6f-8179-bd0e-cccc2c72aea9']

with driver.session() as session:
    for cid in ids:
        res = session.run("MATCH (c:Candidate {id: $id})-[r]->(s:Skill) RETURN s.name as name, type(r) as rel", id=cid).data()
        print(f"ID: {cid} | Skills count: {len(res)}")
        for r in res[:3]:
            print(f"  - {r['name']} ({r['rel']})")

driver.close()
