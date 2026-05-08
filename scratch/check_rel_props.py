import json
from neo4j import GraphDatabase

secrets = json.load(open('secrets.json'))
driver = GraphDatabase.driver(secrets['NEO4J_URI'], auth=(secrets['NEO4J_USERNAME'], secrets['NEO4J_PASSWORD']))
with driver.session() as session:
    query = 'MATCH (c:Candidate {name_kr: "강기태"})-[r]->(s:Skill {name: "Global_Sales_and_Marketing"}) RETURN type(r) as rel_type, properties(r) as props'
    res = session.run(query).single()
    if res:
        print(f"Relationship Type: {res['rel_type']}")
        print(f"Properties: {res['props']}")
    else:
        print("Edge not found.")
driver.close()
