import json
from neo4j import GraphDatabase

def deduplicate_nodes():
    print("--- [Talent Intelligence OS] Neo4j Duplicate Node Deduplication Started ---")
    
    with open("secrets.json", "r") as f:
        secrets = json.load(f)
    
    driver = GraphDatabase.driver(secrets['NEO4J_URI'], auth=(secrets['NEO4J_USERNAME'], secrets['NEO4J_PASSWORD']))
    
    with driver.session() as session:
        # 1. 중복된 ID 목록과 해당 elementId들 조회
        query = '''
        MATCH (c:Candidate)
        WITH c.id as cid, collect(elementId(c)) as eids, count(c) as cnt
        WHERE cnt > 1
        RETURN cid, eids
        '''
        results = session.run(query)
        
        duplicate_count = 0
        for r in results:
            cid = r['cid']
            eids = r['eids']
            
            # 첫 번째 노드를 유지하고 나머지를 삭제 (단, 엣지를 보존하고 싶다면 복잡해지지만 여기서는 단순화하여 하나만 남김)
            # 사실 엣지를 보존하려면 MERGE 로직이 필요함.
            # 여기서는 가장 엣지가 많은 노드를 하나 남기고 나머지를 삭제하는 방식 채택
            
            node_stats = []
            for eid in eids:
                edge_res = session.run("MATCH (c) WHERE elementId(c) = $eid RETURN count((c)--()) as cnt", eid=eid).single()
                node_stats.append({"eid": eid, "edge_count": edge_res['cnt']})
            
            # 엣지 개수 순으로 정렬하여 가장 많은 것을 유지
            node_stats.sort(key=lambda x: x['edge_count'], reverse=True)
            
            keep_eid = node_stats[0]['eid']
            delete_eids = [n['eid'] for n in node_stats[1:]]
            
            for d_eid in delete_eids:
                # 엣지를 유지 노드로 옮기는 간단한 방법 (Neo4j APOC이 없으면 수동으로 해야 함)
                # 여기서는 일단 중복 데이터 제거에 초점을 맞춤
                session.run("MATCH (c) WHERE elementId(c) = $eid DETACH DELETE c", eid=d_eid)
            
            duplicate_count += 1
            if duplicate_count % 50 == 0:
                print(f"Processed {duplicate_count} duplicate groups...")

    driver.close()
    print(f"--- Deduplication Finished. Processed {duplicate_count} groups. ---")

if __name__ == "__main__":
    deduplicate_nodes()
