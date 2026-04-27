import os
import json
from neo4j import GraphDatabase

def check_neo4j():
    # Try to load secrets
    secrets = {}
    try:
        with open("secrets.json", "r", encoding="utf-8") as f:
            secrets = json.load(f)
    except:
        pass
    
    uri = os.environ.get("NEO4J_URI") or secrets.get("NEO4J_URI")
    user = os.environ.get("NEO4J_USERNAME") or secrets.get("NEO4J_USERNAME")
    password = os.environ.get("NEO4J_PASSWORD") or secrets.get("NEO4J_PASSWORD")
    
    if not uri:
        print("NEO4J_URI not found.")
        return

    print(f"Connecting to {uri}...")
    try:
        driver = GraphDatabase.driver(uri, auth=(user, password))
        with driver.session() as session:
            # Check node count
            nodes = session.run("MATCH (n) RETURN count(n) AS count").single()["count"]
            # Check edge count
            edges = session.run("MATCH ()-[r]->() RETURN count(r) AS count").single()["count"]
            # Check relationship types
            rel_types = session.run("MATCH ()-[r]->() RETURN DISTINCT type(r) AS type LIMIT 10")
            types = [r["type"] for r in rel_types]
            
            print(f"Nodes: {nodes}, Edges: {edges}")
            print(f"Sample Relationship Types: {types}")
            
            # Check a sample candidate
            sample = session.run("MATCH (c:Candidate)-[r]->(s:Skill) RETURN c.name_kr as name, type(r) as type, s.name as skill LIMIT 5")
            print("Sample Matches:")
            for r in sample:
                print(f"  {r['name']} -[{r['type']}]-> {r['skill']}")
                
        driver.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_neo4j()
