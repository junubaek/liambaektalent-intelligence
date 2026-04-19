from neo4j import GraphDatabase

def check_db():
    driver = GraphDatabase.driver("bolt://127.0.0.1:7687", auth=("neo4j", "toss1234"))
    
    with driver.session() as session:
        print("==================================================")
        print("1. 실제 존재하는 엣지 타입 전체 목록")
        q1 = "CALL db.relationshipTypes()"
        res1 = session.run(q1)
        for r in res1:
            print(r["relationshipType"])
            
        print("\n==================================================")
        print("2. Candidate 노드에서 나가는 엣지 타입 확인")
        q2 = """
        MATCH (c:Candidate)-[r]->()
        RETURN DISTINCT type(r) AS r_type, count(r) AS cnt
        ORDER BY cnt DESC
        LIMIT 10
        """
        res2 = session.run(q2)
        for r in res2:
            print(f"type: {r['r_type']}, count: {r['cnt']}")
            
        print("\n==================================================")
        print("3. 샘플 1명 엣지 확인 ('김대중')")
        q3 = """
        MATCH (c:Candidate)-[r]->(s)
        WHERE c.name_kr = '김대중'
        RETURN type(r) AS r_type, s.name AS s_name
        LIMIT 10
        """
        res3 = session.run(q3)
        for r in res3:
            print(f"[{r['r_type']}] -> {r['s_name']}")
            
        print("==================================================")
        
    driver.close()

if __name__ == '__main__':
    check_db()
