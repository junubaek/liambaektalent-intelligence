
import os
from neo4j import GraphDatabase

n_uri = os.environ.get('NEO4J_URI', 'bolt://127.0.0.1:7687')
n_user = os.environ.get('NEO4J_USERNAME', 'neo4j')
n_pw = os.environ.get('NEO4J_PASSWORD', 'toss1234')

driver = GraphDatabase.driver(n_uri, auth=(n_user, n_pw))
try:
    with driver.session() as session:
        print("--- 32*/33* Nodes ---")
        res = session.run('MATCH (c:Candidate) WHERE (c.id STARTS WITH "32" OR c.id STARTS WITH "33") RETURN count(c) as total, count(c.embedding) as with_emb')
        data = res.single().data()
        print(data)
        
        print("\n--- Other Nodes ---")
        res = session.run('MATCH (c:Candidate) WHERE NOT (c.id STARTS WITH "32" OR c.id STARTS WITH "33") RETURN count(c) as total, count(c.embedding) as with_emb')
        data = res.single().data()
        print(data)
finally:
    driver.close()
