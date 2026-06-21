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

def check_specific():
    names = ['이석현', '박지민', '전형준', '전예찬']
    with driver.session() as session:
        for name in names:
            print(f"\n--- Checking for '{name}' ---")
            q = "MATCH (c:Candidate) WHERE c.name CONTAINS $name OR c.name_kr CONTAINS $name RETURN c.id AS id, c.name AS name, c.sector AS sector"
            res = session.run(q, name=name)
            rows = list(res)
            if not rows:
                print(f"No candidate found matching '{name}'")
            for r in rows:
                print(f"ID: {r['id']} | Name: {r['name']} | Sector: {r['sector']}")
                # Get edges
                q_edges = "MATCH (c:Candidate {id: $id})-[r]->(s:Skill) RETURN type(r) AS rel, s.name AS skill, r.confidence AS conf"
                edges = session.run(q_edges, id=r['id'])
                for e in edges:
                    print(f"  -> [{e['rel']}] -> {e['skill']} (conf: {e['conf']})")

if __name__ == "__main__":
    check_specific()
    driver.close()
