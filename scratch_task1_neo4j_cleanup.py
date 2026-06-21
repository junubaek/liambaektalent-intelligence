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

def delete_edges():
    delete_q = """
    MATCH (c:Candidate)-[r]->(s:Skill)
    WHERE (c.name = '이정수' OR c.name_kr = '이정수')
      AND s.name IN ['Kernel parameter tuning', 'Firmware', 'Sys_Software']
    DELETE r
    """
    
    count_q = """
    MATCH (c:Candidate)-[r]->(s:Skill)
    WHERE c.name = '이정수' OR c.name_kr = '이정수'
    RETURN count(r) AS active_edges
    """
    
    list_q = """
    MATCH (c:Candidate)-[r]->(s:Skill)
    WHERE c.name = '이정수' OR c.name_kr = '이정수'
    RETURN type(r) AS rel, s.name AS skill
    """

    with driver.session() as session:
        # 1. Delete edges
        print("Deleting wrong edges for 이정수...")
        session.run(delete_q)
        print("Deletion complete.")
        
        # 2. Get active edges count
        res_cnt = session.run(count_q)
        cnt = res_cnt.single()['active_edges']
        print(f"Edges remaining for 이정수: {cnt}")
        
        # 3. List remaining edges
        res_list = session.run(list_q)
        for rec in res_list:
            print(f"  -> [{rec['rel']}] -> {rec['skill']}")

if __name__ == "__main__":
    delete_edges()
    driver.close()
