import json
from neo4j import GraphDatabase

secrets = json.load(open('secrets.json'))
driver = GraphDatabase.driver(secrets['NEO4J_URI'], auth=(secrets['NEO4J_USERNAME'], secrets['NEO4J_PASSWORD']))
with driver.session() as session:
    # 1. 단순히 노드 목록 조회
    query = 'MATCH (c:Candidate {name_kr: "강기태"}) RETURN c.id as id, c.current_company as company'
    results = session.run(query)
    print("[Candidates named Kang Ki-tae in Neo4j]")
    nodes = []
    for r in results:
        nodes.append({"id": r['id'], "company": r['company']})
        print(f" - ID: {r['id']} | Company: {r['company']}")
    
    # 2. 각 ID별 엣지 개수 확인
    for node in nodes:
        edge_query = 'MATCH (c:Candidate {id: $cid})-[r]-() RETURN count(r) as cnt'
        cnt = session.run(edge_query, cid=node['id']).single()['cnt']
        print(f"   -> Edge count for {node['id']}: {cnt}")
driver.close()
