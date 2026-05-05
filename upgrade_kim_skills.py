import json
from neo4j import GraphDatabase

with open("secrets.json", "r") as f:
    secrets = json.load(f)

driver = GraphDatabase.driver(secrets["NEO4J_URI"], auth=(secrets["NEO4J_USERNAME"], secrets["NEO4J_PASSWORD"]))

cid = "f5875fc2-99aa-4605-9742-5ec93f4cd51a"

with driver.session() as session:
    # Upgrade all edges to MANAGED
    session.run("""
        MATCH (c:Candidate {id: $cid})-[r]->(s:Skill)
        DELETE r
        WITH c, s
        CREATE (c)-[:MANAGED]->(s)
    """, cid=cid)
    
    # Add a few more high-value CFO skills if they don't exist
    extra_skills = ["Chief_Financial_Officer", "Investor_Relations", "Tax_Accounting", "Mergers_and_Acquisitions", "IPO_Preparation_and_Execution"]
    for sname in extra_skills:
        session.run("""
            MATCH (c:Candidate {id: $cid})
            MERGE (s:Skill {name: $sname})
            MERGE (c)-[:MANAGED]->(s)
        """, cid=cid, sname=sname)

driver.close()
print("Candidate skills upgraded and boosted in Remote Neo4j.")
