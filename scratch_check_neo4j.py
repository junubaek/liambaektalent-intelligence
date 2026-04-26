
import os
from neo4j import GraphDatabase

n_uri = os.environ.get('NEO4J_URI', 'bolt://127.0.0.1:7687')
n_user = os.environ.get('NEO4J_USERNAME', 'neo4j')
n_pw = os.environ.get('NEO4J_PASSWORD', 'toss1234')

driver = GraphDatabase.driver(n_uri, auth=(n_user, n_pw))
try:
    with driver.session() as session:
        # Check if is_duplicate property exists
        res = session.run("MATCH (c:Candidate) WHERE c.is_duplicate IS NOT NULL RETURN c.is_duplicate as val, count(*) as cnt")
        print("is_duplicate property stats:")
        for r in res:
            print(f"Value: {r['val']}, Count: {r['cnt']}")
            
        # Check if is_duplicate exists at all
        res = session.run("MATCH (c:Candidate) RETURN count(c) as total")
        print(f"Total candidates: {res.single()['total']}")
        
        res = session.run("MATCH (c:Candidate) WHERE c.is_duplicate IS NULL RETURN count(c) as no_prop")
        print(f"Candidates with no is_duplicate property: {res.single()['no_prop']}")

        # Check seniority values
        res = session.run("MATCH (c:Candidate) RETURN c.seniority as val, count(*) as cnt ORDER BY cnt DESC LIMIT 10")
        print("\nSeniority values:")
        for r in res:
            print(f"Value: {r['val']}, Count: {r['cnt']}")
finally:
    driver.close()
