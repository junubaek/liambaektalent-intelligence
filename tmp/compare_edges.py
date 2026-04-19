import sys
from neo4j import GraphDatabase

sys.stdout.reconfigure(encoding='utf-8')

uri = "bolt://127.0.0.1:7687"
auth = ("neo4j", "toss1234")

try:
    driver = GraphDatabase.driver(uri, auth=auth)
    with driver.session() as session:
        # 1. 하정근
        print("=== [1위] 하정근 님 전체 엣지 목록 ===")
        res1 = session.run("""
            MATCH (c:Candidate)-[r]->(s:Skill)
            WHERE c.name_kr = '하정근'
            RETURN type(r) as rel, s.name as skill
            ORDER BY s.name, type(r)
        """)
        rec1 = list(res1)
        print(f"Total Edges: {len(rec1)}")
        for r in rec1:
            print(f"- [{r['rel']}] -> ({r['skill']})")
        
        print("\n" + "="*40 + "\n")
        
        # 2. 김대중
        print("=== [20위] 김대중 님 전체 엣지 목록 ===")
        res2 = session.run("""
            MATCH (c:Candidate)-[r]->(s:Skill)
            WHERE c.name_kr = '김대중'
            RETURN type(r) as rel, s.name as skill
            ORDER BY s.name, type(r)
        """)
        rec2 = list(res2)
        print(f"Total Edges: {len(rec2)}")
        for r in rec2:
            print(f"- [{r['rel']}] -> ({r['skill']})")
            
except Exception as e:
    print(f"Error querying Neo4j: {e}")
finally:
    driver.close()
