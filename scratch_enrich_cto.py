import json
import sqlite3
from neo4j import GraphDatabase

def main():
    # 1. Update SQLite to mark the duplicate record of 안유리 as duplicate
    conn = sqlite3.connect('candidates.db')
    cur = conn.cursor()
    cur.execute("""
        UPDATE candidates 
        SET is_duplicate = 1 
        WHERE id = '31f22567-1b6f-8135-a0ec-c1884ce32120'
    """)
    print("SQLite: Marked duplicate 안유리 (31f22567) as is_duplicate = 1. Rows affected:", cur.rowcount)
    conn.commit()
    conn.close()

    # 2. Connect to Neo4j and add core skill relationships for 이강원 and 안유리
    with open('secrets.json', 'r', encoding='utf-8') as f:
        secrets = json.load(f)

    driver = GraphDatabase.driver(
        secrets['NEO4J_URI'],
        auth=(secrets['NEO4J_USERNAME'], secrets['NEO4J_PASSWORD'])
    )

    with driver.session() as session:
        # Add CTO / Chief_Technology_Officer skills for 이강원
        print("\n=== Neo4j: Merging CTO skills for 이강원 ===")
        session.run("""
            MATCH (c:Candidate) WHERE c.name_kr = '이강원'
            MERGE (s1:Skill {name: 'CTO'})
            MERGE (s2:Skill {name: 'Chief_Technology_Officer'})
            MERGE (c)-[:MANAGED {weight: 1.0}]->(s1)
            MERGE (c)-[:MANAGED {weight: 1.0}]->(s2)
        """)
        print("이강원 CTO 엣지 추가 완료.")

        # Add Technical_Program_Management / Program_Manager skills for 안유리
        print("\n=== Neo4j: Merging TPM skills for 안유리 ===")
        session.run("""
            MATCH (c:Candidate) WHERE c.name_kr = '안유리'
            MERGE (s1:Skill {name: 'Technical_Program_Management'})
            MERGE (s2:Skill {name: 'Program_Manager'})
            MERGE (c)-[:MANAGED {weight: 1.0}]->(s1)
            MERGE (c)-[:MANAGED {weight: 1.0}]->(s2)
        """)
        print("안유리 TPM 엣지 추가 완료.")

    driver.close()
    print("\nEnrichment completed successfully.")

if __name__ == "__main__":
    main()
