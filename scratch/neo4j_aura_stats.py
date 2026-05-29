import json
from neo4j import GraphDatabase

secrets_path = r"C:\Users\cazam\Downloads\이력서자동분석검색시스템\secrets.json"
with open(secrets_path, "r", encoding="utf-8") as f:
    secrets = json.load(f)

n_uri = secrets.get("NEO4J_URI")
n_user = secrets.get("NEO4J_USERNAME")
n_pw = secrets.get("NEO4J_PASSWORD")

driver = GraphDatabase.driver(n_uri, auth=(n_user, n_pw))
with driver.session() as session:
    res = session.run("MATCH (n) RETURN count(n)")
    total_nodes = res.single()[0]
    
    res = session.run("MATCH ()-[r]->() RETURN count(r)")
    total_edges = res.single()[0]
    
    res = session.run("MATCH (c:Candidate) RETURN count(c)")
    total_candidates = res.single()[0]
    
    res = session.run("MATCH (s:Skill) RETURN count(s)")
    total_skills = res.single()[0]
    
    print("\n=== Neo4j Aura Status ===")
    print(f"Total Nodes: {total_nodes}")
    print(f"Total Edges: {total_edges}")
    print(f"Total Candidates: {total_candidates}")
    print(f"Total Skills: {total_skills}")
    
driver.close()
