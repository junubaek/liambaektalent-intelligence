import json
from neo4j import GraphDatabase

def main():
    # Load secrets
    with open('secrets.json', 'r', encoding='utf-8') as f:
        secrets = json.load(f)

    driver = GraphDatabase.driver(
        secrets['NEO4J_URI'],
        auth=(secrets['NEO4J_USERNAME'], secrets['NEO4J_PASSWORD'])
    )

    with driver.session() as session:
        # [작업 1] 이강원 Neo4j 엣지 추가
        print("=== [작업 1] 이강원 Neo4j 엣지 추가 ===")
        session.run("""
            MATCH (c:Candidate) WHERE c.name_kr = '이강원'
            MERGE (s1:Skill {name: 'Platform_Operations_Planning'})
            MERGE (s2:Skill {name: 'MLOps'})
            MERGE (s3:Skill {name: 'Infrastructure_and_Cloud'})
            MERGE (s4:Skill {name: 'Product_Service_Planning'})
            MERGE (s5:Skill {name: 'Agile_Methodology'})
            MERGE (c)-[:MANAGED {weight: 1.0}]->(s1)
            MERGE (c)-[:MANAGED {weight: 0.9}]->(s2)
            MERGE (c)-[:MANAGED {weight: 0.9}]->(s3)
            MERGE (c)-[:DESIGNED {weight: 0.85}]->(s4)
            MERGE (c)-[:MANAGED {weight: 0.85}]->(s5)
        """)
        print("이강원 Neo4j 엣지 생성 완료.")

        # [작업 2] 안유리 현재 상태 확인 및 엣지 추가
        print("\n=== [작업 2] 안유리 현재 상태 확인 ===")
        res = session.run("""
            MATCH (c:Candidate {name_kr: '안유리'})-[r]->(s:Skill)
            RETURN type(r), s.name
        """)
        records = list(res)
        print(f"Found {len(records)} existing edges for 안유리:")
        for r in records:
            print(f"  - [{r[0]}] -> {r[1]}")

        print("\n=== [작업 2] 안유리 Neo4j 엣지 추가 ===")
        session.run("""
            MATCH (c:Candidate) WHERE c.name_kr = '안유리'
            MERGE (s1:Skill {name: 'Agile_Methodology'})
            MERGE (s2:Skill {name: 'Product_Service_Planning'})
            MERGE (s3:Skill {name: 'Platform_Operations_Planning'})
            MERGE (s4:Skill {name: 'Product_Manager'})
            MERGE (c)-[:MANAGED {weight: 1.0}]->(s1)
            MERGE (c)-[:BUILT {weight: 0.9}]->(s2)
            MERGE (c)-[:MANAGED {weight: 0.9}]->(s3)
            MERGE (c)-[:MANAGED {weight: 0.85}]->(s4)
        """)
        print("안유리 Neo4j 엣지 생성 완료.")

    driver.close()
    print("\nNeo4j updates completed successfully.")

if __name__ == "__main__":
    main()
