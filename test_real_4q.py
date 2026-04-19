import json
from jd_compiler import api_search_v8, parse_jd_to_json, deduplicate_conditions, apply_downgrade_map, inject_node_affinity
from neo4j import GraphDatabase

driver = GraphDatabase.driver("bolt://127.0.0.1:7687", auth=("neo4j", "toss1234"))

queries = [
    'vLLM PyTorch',
    'Kubernetes DevOps',
    '연결회계 IFRS',
    'Treasury FX Risk'
]

def format_matched_skills(session, name, target_skills):
    cypher = """
    MATCH (c:Candidate {name_kr: $name})-[rel]->(s:Skill)
    RETURN s.name AS skill, type(rel) AS action
    """
    edges_res = session.run(cypher, name=name)
    matched = []
    
    # Identify which skills actually exist in the DB for this candidate and match the query target
    for edge in edges_res:
        s_name = edge['skill']
        action = edge['action']
        if s_name.lower() in target_skills:
            matched.append(f"{s_name}({action})")
            
    return ", ".join(matched) if matched else "No direct matches (Prefilter/Graph matched internally but possibly lowercase mismatch)"

with driver.session() as session:
    for q in queries:
        print(f"==================================================")
        print(f"🔍 [Query] : {q}")
        print(f"==================================================")
        
        # 1. 쿼리 파싱을 통해 타겟 노드(Skill) 추출
        extracted = parse_jd_to_json(q)
        conds = extracted.get("conditions", [])
        conds = deduplicate_conditions(conds)
        conds = apply_downgrade_map(conds)
        conds = inject_node_affinity(conds)
        target_skills = [c['skill'].lower() for c in conds]
        
        # 2. V8 검색
        res_dict = api_search_v8(q)
        top5 = res_dict.get('matched', [])[:5]
        
        if not top5:
            print("❌ 검색 결과 없음\n")
            continue
            
        # 3. Top-5 결과 및 후보자별 매칭 스킬 출력
        for i, r in enumerate(top5):
            name = r['name_kr']
            score = r['score']
            matched_str = format_matched_skills(session, name, target_skills)
            print(f"[{i+1}위] {name}  (Score: {score})")
            print(f"       ► 매칭 스킬: {matched_str}")
        print("\n")
