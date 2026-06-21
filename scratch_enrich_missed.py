import json
import sqlite3
from neo4j import GraphDatabase

def main():
    # Load secrets
    with open('secrets.json', 'r', encoding='utf-8') as f:
        secrets = json.load(f)

    # 1. Update SQLite Profile Summary for 이강원
    db_path = "candidates.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("=== SQLite Updates ===")
    enrich_summary = (
        "Meta Reality Labs 및 Google Wear OS 기술 총괄 TPM. "
        "오늘의집 CTO로 플랫폼 기술 전략 수립 및 엔지니어링 조직 리딩. "
        "16년 경력의 기술 임원으로 AR/웨어러블/모바일 플랫폼 기술 로드맵 설계 및 글로벌 파트너십 구축 전문가."
    )
    cursor.execute("""
        UPDATE candidates 
        SET profile_summary = ? 
        WHERE name_kr = '이강원' AND is_duplicate = 0
    """, (enrich_summary,))
    print(f"Updated 이강원 profile_summary. Rows affected: {cursor.rowcount}")
    conn.commit()
    conn.close()

    # 2. Connect to Neo4j and perform updates
    driver = GraphDatabase.driver(
        secrets['NEO4J_URI'],
        auth=(secrets['NEO4J_USERNAME'], secrets['NEO4J_PASSWORD'])
    )

    with driver.session() as session:
        print("\n=== Neo4j: Checking 정혜연 edges ===")
        res = session.run("""
            MATCH (c:Candidate {name_kr: '정혜연'})-[r]->(s:Skill)
            RETURN type(r), s.name
        """)
        records = list(res)
        print(f"Found {len(records)} existing edges for 정혜연:")
        for r in records:
            print(f"  - [{r[0]}] -> {r[1]}")

        # Adding edges for 정혜연
        print("\n=== Neo4j: Merging edges for 정혜연 ===")
        session.run("""
            MATCH (c:Candidate) WHERE c.name_kr = '정혜연'
            MERGE (s1:Skill {name: 'Kafka'})
            MERGE (s2:Skill {name: 'Kubernetes'})
            MERGE (s3:Skill {name: 'Infrastructure_and_Cloud'})
            MERGE (s4:Skill {name: 'Data_Pipeline_Construction'})
            MERGE (c)-[:BUILT {weight: 1.0}]->(s1)
            MERGE (c)-[:BUILT {weight: 0.9}]->(s2)
            MERGE (c)-[:MANAGED {weight: 0.9}]->(s3)
            MERGE (c)-[:BUILT {weight: 0.85}]->(s4)
        """)
        print("정혜연 edges merged successfully.")

        # Adding edges for 김은형
        print("\n=== Neo4j: Merging edges for 김은형 ===")
        session.run("""
            MATCH (c:Candidate) WHERE c.name_kr = '김은형' AND c.current_company CONTAINS 'SM'
            MERGE (s1:Skill {name: 'Mergers_and_Acquisitions'})
            MERGE (s2:Skill {name: 'Corporate_Finance'})
            MERGE (s3:Skill {name: 'Financial_Accounting'})
            MERGE (s4:Skill {name: 'IPO_Preparation'})
            MERGE (s5:Skill {name: 'IR_Management'})
            MERGE (c)-[:MANAGED {weight: 1.0}]->(s1)
            MERGE (c)-[:MANAGED {weight: 0.95}]->(s2)
            MERGE (c)-[:MANAGED {weight: 0.9}]->(s3)
            MERGE (c)-[:BUILT {weight: 0.85}]->(s4)
            MERGE (c)-[:MANAGED {weight: 0.85}]->(s5)
        """)
        print("김은형 edges merged successfully.")

    driver.close()
    print("\nEnrichment updates completed successfully.")

if __name__ == "__main__":
    main()
