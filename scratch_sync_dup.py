import os
from neo4j import GraphDatabase

n_uri = os.environ.get('NEO4J_URI', 'bolt://localhost:7687')
n_user = os.environ.get('NEO4J_USERNAME', 'neo4j')
n_pw = os.environ.get('NEO4J_PASSWORD', 'toss1234')

driver = GraphDatabase.driver(n_uri, auth=(n_user, n_pw))

def sync():
    with driver.session() as session:
        # Set old one to dup=1
        session.run("MATCH (c:Candidate {id: '33522567-1b6f-81a3-ac63-e62ab98e6793'}) SET c.is_duplicate = 1")
        # Set new one to dup=0
        session.run("MATCH (c:Candidate {id: '95207af2-552f-43ad-afcb-4d883fbacbb6'}) SET c.is_duplicate = 0")
    print('Neo4j sync complete')

sync()
driver.close()
