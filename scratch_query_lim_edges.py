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

def run_edges():
    q = """
    MATCH (c:Candidate)-[r]->(s:Skill)
    WHERE c.name_kr = '임병진' OR c.name = '임병진'
    RETURN type(r) AS rel, s.name AS skill, coalesce(r.weight, r.confidence) AS score
    ORDER BY score DESC
    """
    with driver.session() as session:
        res = session.run(q)
        print("=== [1] 임병진 Neo4j Edges ===")
        records = list(res)
        if not records:
            print("No edges found for 임병진.")
        else:
            for rec in records:
                score_str = f"{rec['score']}" if rec['score'] is not None else "None"
                print(f"  -> [{rec['rel']}] -> {rec['skill']} (Weight: {score_str})")

if __name__ == "__main__":
    run_edges()
    driver.close()
