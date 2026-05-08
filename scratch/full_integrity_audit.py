import sqlite3
import json
from neo4j import GraphDatabase

def run_full_audit():
    print("--- [Talent Intelligence OS] Neo4j Full Integrity Audit Started ---")
    
    # 1. SQLite에서 기준 데이터 로드
    conn = sqlite3.connect('candidates.db')
    cur = conn.cursor()
    cur.execute("SELECT id, name_kr, current_company FROM candidates WHERE is_duplicate = 0")
    sqlite_data = {row[0]: {"name": row[1], "company": row[2]} for row in cur.fetchall()}
    conn.close()
    print(f"SQLite Master Records: {len(sqlite_data)} candidates loaded.")

    # 2. Neo4j 연결
    with open("secrets.json", "r") as f:
        secrets = json.load(f)
    
    driver = GraphDatabase.driver(secrets['NEO4J_URI'], auth=(secrets['NEO4J_USERNAME'], secrets['NEO4J_PASSWORD']))
    
    audit_report = {
        "ghost_nodes": [],
        "conflict_nodes": [],
        "duplicates": []
    }

    with driver.session() as session:
        # 모든 Candidate 노드 조회
        res = session.run("MATCH (c:Candidate) RETURN c.id as id, c.name_kr as name, c.current_company as company, elementId(c) as eid")
        
        id_node_map = {} # {id: [eid1, eid2, ...]}
        
        for r in res:
            cid = r['id']
            cname = r['name']
            ccompany = r['company']
            eid = r['eid']
            
            if cid not in id_node_map:
                id_node_map[cid] = []
            id_node_map[cid].append({"eid": eid, "name": cname, "company": ccompany})

            # Case A: Ghost Node (ID not in SQLite)
            if cid not in sqlite_data:
                audit_report["ghost_nodes"].append({"id": cid, "name": cname, "company": ccompany, "eid": eid})
                continue
            
            # Case B: Conflict Node (ID exists but company/name mismatch)
            master = sqlite_data[cid]
            # 회사명이 None이거나 다른 경우 정밀 체크 (단순 인코딩/공백 차이 고려)
            if cname != master["name"]:
                 audit_report["conflict_nodes"].append({"id": cid, "master_name": master["name"], "node_name": cname, "eid": eid})
            elif ccompany != master["company"] and master["company"] is not None and ccompany is not None:
                # 단순 포함 여부로 체크 (유연한 매칭)
                if master["company"] not in ccompany and ccompany not in master["company"]:
                    audit_report["conflict_nodes"].append({"id": cid, "master_company": master["company"], "node_company": ccompany, "eid": eid})

        # Case C: Multiple nodes with same ID
        for cid, nodes in id_node_map.items():
            if len(nodes) > 1:
                audit_report["duplicates"].append({"id": cid, "nodes": nodes})

    print(f"\n[Audit Result Summary]")
    print(f" - Ghost Nodes: {len(audit_report['ghost_nodes'])}")
    print(f" - Conflict Nodes: {len(audit_report['conflict_nodes'])}")
    print(f" - ID Duplicates: {len(audit_report['duplicates'])}")

    # 3. 정제 작업 (Delete)
    with driver.session() as session:
        # 1) Ghost Nodes 삭제
        if audit_report["ghost_nodes"]:
            print("\nDeleting Ghost Nodes...")
            for ghost in audit_report["ghost_nodes"]:
                session.run("MATCH (c) WHERE elementId(c) = $eid DETACH DELETE c", eid=ghost["eid"])
                print(f"  - Deleted Ghost: {ghost['name']} ({ghost['id']})")

        # 2) Conflict Nodes 삭제 (정답 노드가 따로 있는 경우만)
        if audit_report["conflict_nodes"]:
            print("\nDeleting Conflict Nodes...")
            for conflict in audit_report["conflict_nodes"]:
                # 해당 ID를 가진 노드 중 정답 노드가 리스트에 따로 있는지 확인
                cid = conflict["id"]
                all_nodes = id_node_map.get(cid, [])
                has_correct_node = any(n["name"] == sqlite_data[cid]["name"] and 
                                       (sqlite_data[cid]["company"] is None or n["company"] == sqlite_data[cid]["company"]) 
                                       for n in all_nodes)
                
                if has_correct_node:
                    session.run("MATCH (c) WHERE elementId(c) = $eid DETACH DELETE c", eid=conflict["eid"])
                    print(f"  - Deleted Conflict: {conflict.get('node_name', 'Unknown')} at {conflict.get('node_company', 'Unknown')}")
                else:
                    print(f"  - Kept Conflict (No better match found): {conflict.get('node_name')} ({cid})")

    driver.close()
    print("\n--- Audit and Cleanup Finished ---")

if __name__ == "__main__":
    run_full_audit()
