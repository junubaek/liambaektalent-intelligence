import json
from neo4j import GraphDatabase

secrets = json.load(open('secrets.json'))
driver = GraphDatabase.driver(secrets['NEO4J_URI'], auth=(secrets['NEO4J_USERNAME'], secrets['NEO4J_PASSWORD']))

mapping = {
    '898ea4e0-77d4-46d5-bf4d-c2d5b4a04741': ['Sales_Core', 'Overseas', 'Manager', 'Global_Sales_and_Marketing', 'B2B_Sales'],
    'db752f0f-0f1a-437c-a09d-43c20442ab7b': ['General_Affairs', 'Manager', 'Procurement_Buyer', 'Asset_Management', 'Administrative_Management'],
    '55726c4a-4601-4ee9-87dc-581d15eda75e': ['Bioinformatics', 'Engineer', 'Machine_Learning', 'Data_Science']
}

with driver.session() as session:
    for cid, skills in mapping.items():
        print(f"Setting skills to BUILT for {cid}...")
        session.run("MATCH (c:Candidate {id: $id})-[r]->(s:Skill) DELETE r", id=cid)
        for sname in skills:
            session.run("""
                MATCH (c:Candidate {id: $id})
                MERGE (s:Skill {name: $sname})
                MERGE (c)-[:BUILT]->(s)
            """, id=cid, sname=sname)
        print(f"  Done.")

driver.close()
