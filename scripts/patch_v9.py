import re

with open("jd_compiler.py", "r", encoding="utf-8") as f:
    content = f.read()

v9_code = """
# =======================================================================
# [V8.9] 2-Stage 하이브리드 통합 엔진 (Vector Recall + Graph Precision)
# =======================================================================
def normalize_query_with_map(raw_keywords):
    \"\"\"
    [어휘 불일치 해결 1단계] 사용자 입력(A)을 시스템 표준 노드(A')로 강제 변환
    \"\"\"
    from ontology_graph import CANONICAL_MAP
    canonical_targets = set()
    for word in raw_keywords:
        canonical_word = CANONICAL_MAP.get(word, CANONICAL_MAP.get(word.upper(), word))
        canonical_targets.add(canonical_word)
    return list(canonical_targets)

def api_search_v9(prompt: str, session_id: str = None) -> list:
    import math
    from connectors.openai_api import OpenAIClient
    
    st = time.time()
    logger.info(f"\\n\\n[V8.9 API Search] Payload: {prompt} / Session: {session_id}")
    
    # 1. LLM Query Expansion
    openai = OpenAIClient(secret_data.get("OPENAI_API_KEY", ""))
    system_prompt = "주어진 사용자의 직무/스킬 요구사항을 분석하여 1536차원 벡터 검색에 유리하게 연관 스킬 키워드들로 확장된 영어 명사 위주의 검색 쿼리로 변환해."
    expanded_query_text = openai.get_chat_completion(system_prompt, prompt)
    if not expanded_query_text: expanded_query_text = prompt
    
    # 2. Embedding Generation
    query_vector = openai.embed_content(expanded_query_text)
    if not query_vector:
        logger.error("[V8.9] Embedding generation failed. Falling back to V8.")
        return api_search_v8(prompt, session_id)
        
    # 3. Canonical Target Extraction
    import re
    # 간단한 명사/단어 추출 (형태소 분석 배제)
    raw_keywords = set(re.findall(r'[a-zA-Z0-9가-힣]+', prompt))
    canonical_targets = normalize_query_with_map(list(raw_keywords))
    logger.info(f"[V8.9] 🎯 Graph 조준 타겟 (정규화 완료): {canonical_targets}")

    # ==========================================
    # STAGE 1: Vector Search (High Recall 레이더망)
    # ==========================================
    vector_query = \"\"\"
    CALL db.index.vector.queryNodes('resume_embeddings', 150, $query_vector)
    YIELD node AS candidate, score AS vector_score
    RETURN candidate.id AS candidate_id, candidate.name_kr AS name, vector_score
    \"\"\"
    
    from neo4j import GraphDatabase
    driver = GraphDatabase.driver("bolt://127.0.0.1:7687", auth=("neo4j", "toss1234"))
    with driver.session() as session:
        stage1_results = session.run(vector_query, query_vector=query_vector).data()
        
    if not stage1_results:
        logger.warning("[V8.9] Vector search returned 0 results.")
        return []
        
    candidate_ids = [res['candidate_id'] for res in stage1_results]
    logger.info(f"[V8.9] 📡 Vector 레이더망 포집 완료: {len(candidate_ids)}명 확보")

    # ==========================================
    # STAGE 2: Graph Scoring (High Precision 저격총)
    # ==========================================
    graph_query = \"\"\"
    MATCH (c:Candidate)-[r]->(s:Skill)
    WHERE c.id IN $candidate_ids AND s.name IN $canonical_targets
    RETURN c.id AS candidate_id, c.name_kr AS name, collect({skill: s.name, action: type(r)}) AS edges, 
           size((c)-[]->()) AS total_edges
    \"\"\"
    
    from neo4j import GraphDatabase
    driver = GraphDatabase.driver("bolt://127.0.0.1:7687", auth=("neo4j", "toss1234"))
    with driver.session() as session:
        stage2_results = session.run(graph_query, candidate_ids=candidate_ids, canonical_targets=canonical_targets).data()

    final_candidates = {}
    
    # Init from Vector
    for res in stage1_results:
        final_candidates[res['candidate_id']] = {
            "id": res['candidate_id'],
            "name": res['name'],
            "vector_score": res['vector_score'],
            "graph_score": 0.0,
            "matched_edges": [],
            "total_edges": 0
        }

    # Add Graph Stats
    for res in stage2_results:
        cid = res['candidate_id']
        raw_graph_score = 0.0
        
        for edge in res['edges']:
            action_weight = ACTION_WEIGHTS.get(edge['action'], 1.0)
            raw_graph_score += action_weight
            
        final_graph_score = math.log(max(raw_graph_score, 0) + 1)
        
        if cid in final_candidates:
            final_candidates[cid]["graph_score"] = final_graph_score
            final_candidates[cid]["matched_edges"] = [e['skill'] for e in res['edges']]
            final_candidates[cid]["total_edges"] = res['total_edges']
            
    # STAGE 3: Final Sorting
    sorted_results = sorted(
        final_candidates.values(),
        key=lambda x: (x['graph_score'], x['vector_score'], x['total_edges']),
        reverse=True
    )
    
    logger.info(f"[V8.9] Pipeline latency: {time.time() - st:.3f}s")
    
    # Format to traditional API response
    final_output = []
    for cand in sorted_results[:50]:
        final_output.append({
            "name": cand["name"],
            "hash": cand["id"],
            "score": cand["graph_score"] * 100 + cand["vector_score"],
            "graph_score": cand["graph_score"],
            "vector_score": cand["vector_score"],
            "matched_edges": cand["matched_edges"],
            "total_edges": cand["total_edges"],
            "raw_text": "",
            "summary": "V8.9 Hybrid Evaluated."
        })
        
    return final_output

"""

if "def api_search_v9" not in content:
    content += "\n" + v9_code

import re
# Ensure app/api/main.py uses v9
with open("app/api/main.py", "r", encoding="utf-8") as f:
    main_code = f.read()

if "api_search_v8" in main_code:
    main_code = main_code.replace("api_search_v8", "api_search_v9")
    with open("app/api/main.py", "w", encoding="utf-8") as f:
        f.write(main_code)

with open("jd_compiler.py", "w", encoding="utf-8") as f:
    f.write(content)
    
print("V9 Patch Applied!")

