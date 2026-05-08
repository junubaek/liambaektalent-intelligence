import json
from neo4j import GraphDatabase

with open("secrets.json", "r", encoding="utf-8") as f:
    secrets = json.load(f)

driver = GraphDatabase.driver(secrets["NEO4J_URI"], auth=(secrets["NEO4J_USERNAME"], secrets["NEO4J_PASSWORD"]))
cid = "c3d4ee55-266a-44f6-8e66-fb7486be38a8"

with driver.session() as session:
    res = session.run("""
        MATCH (c:Candidate {id: $id}) 
        RETURN c.name_kr as name, 
               size(c.raw_text) as txt_len, 
               size(c.embedding) as emb_len, 
               left(c.raw_text, 100) as snippet
    """, id=cid).data()
    if res:
        print(f"Candidate: {res[0]['name']}")
        print(f"Text Length: {res[0]['txt_len']}")
        print(f"Embedding Length: {res[0]['emb_len']}")
        print(f"Snippet: {res[0]['snippet']}")
    else:
        print("Candidate Node NOT FOUND in Neo4j by ID.")

driver.close()
