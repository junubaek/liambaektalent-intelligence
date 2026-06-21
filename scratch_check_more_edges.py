import json
import sys
from neo4j import GraphDatabase

sys.stdout.reconfigure(encoding='utf-8')
secrets_path = r"C:\Users\cazam\Downloads\이력서자동분석검색시스템\secrets.json"

with open(secrets_path, "r", encoding="utf-8") as f:
    secrets = json.load(f)

n_uri = secrets.get("NEO4J_URI", "neo4j://127.0.0.1:7687")
n_user = secrets.get("NEO4J_USERNAME", "neo4j")
n_pw = secrets.get("NEO4J_PASSWORD", "toss1234")
driver = GraphDatabase.driver(n_uri, auth=(n_user, n_pw))

def check_nodes():
    q = """
    MATCH (c:Candidate)
    RETURN c.name AS name, c.sector AS sector, c.current_company AS company
    ORDER BY name
    """
    with driver.session() as session:
        print("=== Neo4j Candidate Nodes list ===")
        res = session.run(q)
        for rec in res:
            print(f"Name: {rec['name']} | Sector: {rec['sector']} | Company: {rec['company']}")

if __name__ == "__main__":
    check_nodes()
    driver.close()
