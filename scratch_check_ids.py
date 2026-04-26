
import os
from neo4j import GraphDatabase

n_uri = os.environ.get('NEO4J_URI', 'bolt://127.0.0.1:7687')
n_user = os.environ.get('NEO4J_USERNAME', 'neo4j')
n_pw = os.environ.get('NEO4J_PASSWORD', 'toss1234')

driver = GraphDatabase.driver(n_uri, auth=(n_user, n_pw))
try:
    with driver.session() as session:
        ids = ['31f22567-1b6f-81f3-bfe6-fb7fd7c9ad61', '31f22567-1b6f-8150-8062-f6862dec66e5', '32022567-1b6f-8121-b3b4-dac79d7ece90', '32e22567-1b6f-81c5-8f9e-c02433e25876']
        res = session.run('MATCH (c:Candidate) WHERE c.id IN $ids RETURN c.id as id, c.embedding IS NOT NULL as has_emb', ids=ids)
        for r in res:
            print(f"ID: {r['id']}, Has Embedding: {r['has_emb']}")
finally:
    driver.close()
