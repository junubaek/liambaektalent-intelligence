import json
from neo4j import GraphDatabase

secrets = json.load(open('secrets.json'))
driver = GraphDatabase.driver(secrets['NEO4J_URI'], auth=(secrets['NEO4J_USERNAME'], secrets['NEO4J_PASSWORD']))
with driver.session() as session:
    # 1. 중독푸드 노드 삭제
    delete_query = 'MATCH (c:Candidate {name_kr: "강기태"}) WHERE c.current_company CONTAINS "중독푸드" DETACH DELETE c'
    session.run(delete_query)
    print("중독푸드 강기태 유령 노드 삭제 완료.")
    
    # 2. 결과 확인
    check_query = 'MATCH (c:Candidate {name_kr: "강기태"}) RETURN c.id as id, c.current_company as company'
    results = session.run(check_query)
    print("\n[남아있는 강기태 노드]")
    for r in results:
        print(f" - ID: {r['id']} | Company: {r['company']}")
        
    # 3. 엣지 개수 재확인
    edge_query = 'MATCH (c:Candidate {name_kr: "강기태"})-[r]->(s) RETURN type(r) as rel, s.name as skill'
    edges = session.run(edge_query)
    print("\n[남아있는 엣지 목록]")
    for e in edges:
        print(f" - {e['rel']} -> {e['skill']}")
driver.close()
