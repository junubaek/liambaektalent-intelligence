import json
from neo4j import GraphDatabase

secrets = json.load(open('secrets.json'))
driver = GraphDatabase.driver(secrets['NEO4J_URI'], auth=(secrets['NEO4J_USERNAME'], secrets['NEO4J_PASSWORD']))

mapping = {
    '898ea4e0-77d4-46d5-bf4d-c2d5b4a04741': ['Global_Sales_and_Marketing', 'B2B_Sales', 'Negotiation'],
    'db752f0f-0f1a-437c-a09d-43c20442ab7b': ['General_Affairs', 'Procurement_Buyer', 'Asset_Management', 'Team_Management'],
    '55726c4a-4601-4ee9-87dc-581d15eda75e': ['Bioinformatics', 'Machine_Learning', 'Data_Analysis', 'Python']
}

with driver.session() as session:
    for cid, skills in mapping.items():
        print(f"Setting skills for {cid}...")
        # Add canonical skills with BUILT or MANAGED action
        for sname in skills:
            session.run("""
                MATCH (c:Candidate {id: $id})
                MERGE (s:Skill {name: $sname})
                MERGE (c)-[:MANAGED]->(s)
            """, id=cid, sname=sname)
        print(f"  Done.")

driver.close()
