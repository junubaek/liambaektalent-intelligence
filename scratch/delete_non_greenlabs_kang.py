import json
from neo4j import GraphDatabase

secrets = json.load(open('secrets.json'))
driver = GraphDatabase.driver(secrets['NEO4J_URI'], auth=(secrets['NEO4J_USERNAME'], secrets['NEO4J_PASSWORD']))
with driver.session() as session:
    # 1. 그린랩스가 아닌 강기태 노드 삭제
    delete_query = 'MATCH (c:Candidate {name_kr: "강기태"}) WHERE NOT c.current_company CONTAINS "그린랩스" DETACH DELETE c'
    session.run(delete_query)
    print("그린랩스가 아닌 모든 강기태 노드(유령 데이터) 삭제 시도 완료.")
    
    # 2. 결과 확인
    check_query = 'MATCH (c:Candidate {name_kr: "강기태"}) RETURN c.id as id, c.current_company as company'
    results = session.run(check_query)
    print("\n[남아있는 강기태 노드]")
    node_exists = False
    for r in results:
        node_exists = True
        print(f" - ID: {r['id']} | Company: {r['company']}")
    
    if not node_exists:
        print("경고: 모든 강기태 노드가 삭제되었습니다. 복구가 필요할 수 있습니다.")

    # 3. 엣지 개수 재확인
    edge_query = 'MATCH (c:Candidate {name_kr: "강기태"})-[r]->(s) RETURN type(r) as rel, s.name as skill'
    edges = session.run(edge_query)
    print("\n[남아있는 엣지 목록]")
    for e in edges:
        print(f" - {e['rel']} -> {e['skill']}")
driver.close()
