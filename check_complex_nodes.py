import json
from neo4j import GraphDatabase

NEO4J_URI = "neo4j://127.0.0.1:7687"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "toss1234"

driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))

def check_complex():
    with driver.session() as session:
        query = """
        MATCH (s:Skill)
        WHERE s.name CONTAINS '_and_'
           OR s.name CONTAINS '_or_'
        RETURN s.name as name, count{(s)<-[]-()} as edge_cnt
        ORDER BY edge_cnt DESC
        LIMIT 30
        """
        results = session.run(query)
        print("=== 잔여 복합 명사구 노드 목록 (Top 30) ===")
        for record in results:
            print(f"[{record['edge_cnt']:4d} edges] {record['name']}")

if __name__ == "__main__":
    check_complex()
