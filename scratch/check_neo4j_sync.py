import json
from neo4j import GraphDatabase

def check_neo4j():
    with open('processed_ids.json', 'r') as f:
        ids = json.load(f)
        
    with GraphDatabase.driver('neo4j://127.0.0.1:7687', auth=('neo4j', 'toss1234')) as driver:
        with driver.session() as session:
            result = session.run("MATCH (c:Candidate) WHERE c.id IN $ids RETURN count(c)", ids=ids)
            count = result.single()[0]
            print(f"Candidates in Neo4j: {count} / {len(ids)}")

if __name__ == "__main__":
    check_neo4j()
