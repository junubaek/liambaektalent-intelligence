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

def check_neo4j():
    # 1. Lee Sangsoo
    q1 = """
    MATCH (c:Candidate)-[r]->(s:Skill)
    WHERE c.name = '이정수' OR c.name_kr = '이정수'
    RETURN type(r) AS rel, s.name AS skill
    ORDER BY skill
    """
    
    # 2. Park Yoora, Keum Minguk
    q2 = """
    MATCH (c:Candidate)-[r]->(s:Skill)
    WHERE c.name_kr IN ['박유라', '금민국'] OR c.name IN ['박유라', '금민국']
    RETURN c.name_kr AS name, type(r) AS rel, s.name AS skill
    ORDER BY name, skill
    """

    with driver.session() as session:
        print("=== [1] 이정수 Neo4j Edges ===")
        res1 = session.run(q1)
        count = 0
        for rec in res1:
            print(f"  -> [{rec['rel']}] -> {rec['skill']}")
            count += 1
        print(f"Total edges remaining for 이정수: {count}")
        
        print("\n=== [2] 박유라, 금민국 Neo4j Edges ===")
        res2 = session.run(q2)
        for rec in res2:
            print(f"후보자: {rec['name']} | 관계: {rec['rel']} | 스킬: {rec['skill']}")

if __name__ == "__main__":
    check_neo4j()
    driver.close()
