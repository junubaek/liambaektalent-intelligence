import re
from datetime import datetime

def parse_date(date_str):
    try:
        return datetime.strptime(date_str, "%Y-%m")
    except:
        pass
    try:
        return datetime.strptime(date_str, "%Y-%m-%d")
    except:
        pass
    try:
        return datetime.strptime(date_str, "%Y")
    except:
        pass
    return None

import time

v9_advanced_code = """
def calculate_recency_multiplier(end_date_str):
    from datetime import datetime
    if not end_date_str or '현재' in end_date_str or '재직' in end_date_str or 'present' in end_date_str.lower():
        return 1.2
        
    # Attempt to parse date
    import re
    match = re.search(r'20\d{2}', end_date_str)
    if not match: return 1.0
    
    try:
        year = int(match.group(0))
        current_year = datetime.now().year
        diff = current_year - year
        if diff <= 3: return 1.2
        if diff >= 5: return 0.8
    except:
        pass
    return 1.0

def api_search_v9(prompt: str, session_id: str = None) -> list:
    import math
    import time
    from connectors.openai_api import OpenAIClient
    from neo4j import GraphDatabase
    driver = GraphDatabase.driver("bolt://127.0.0.1:7687", auth=("neo4j", "toss1234"))
    
    st = time.time()
    logger.info(f"\\n\\n[V9.0 Chunk-Level API Search] Payload: {prompt}")
    
    openai = OpenAIClient(secret_data.get("OPENAI_API_KEY", ""))
    system_prompt = "주어진 사용자의 직무/스킬 요구사항을 분석하여 1536차원 벡터 검색에 유리하게 연관 스킬 키워드들로 확장된 영어 명사 위주의 검색 쿼리로 변환해."
    expanded_query_text = openai.get_chat_completion(system_prompt, prompt)
    if not expanded_query_text: expanded_query_text = prompt
    
    query_vector = openai.embed_content(expanded_query_text)
    if not query_vector:
        logger.error("[V9.0] Embedding generation failed.")
        return []
        
    import re
    raw_keywords = set(re.findall(r'[a-zA-Z0-9가-힣]+', prompt))
    canonical_targets = normalize_query_with_map(list(raw_keywords))

    with driver.session() as session:
        # STAGE 1: Vector Search across Experience Chunks
        vector_query = \"\"\"
        CALL db.index.vector.queryNodes('chunk_embeddings', 150, $query_vector)
        YIELD node AS chunk, score AS vector_score
        MATCH (c:Candidate)-[:HAS_EXPERIENCE]->(chunk)
        RETURN c.id AS candidate_id, c.name_kr AS name, chunk.id AS chunk_id, 
               chunk.company_name AS company_name, chunk.end_date AS end_date, vector_score
        \"\"\"
        stage1_results = session.run(vector_query, query_vector=query_vector).data()

        if not stage1_results:
            return []

        chunk_ids = [res['chunk_id'] for res in stage1_results]

        # STAGE 2: Graph Scoring per Chunk
        graph_query = \"\"\"
        MATCH (chunk:Experience_Chunk)-[r]->(s:Skill)
        WHERE chunk.id IN $chunk_ids AND s.name IN $canonical_targets
        RETURN chunk.id AS chunk_id, collect({skill: s.name, action: type(r)}) AS edges, 
               size((chunk)-[]->()) AS total_edges
        \"\"\"
        stage2_results = session.run(graph_query, chunk_ids=chunk_ids, canonical_targets=canonical_targets).data()

    # Organize Graph results mapped to chunks
    graph_map = {res['chunk_id']: res for res in stage2_results}

    # Group by Candidate, keeping the "Best Match Chunk"
    candidates_best_chunk = {}

    for v_res in stage1_results:
        cid = v_res['candidate_id']
        chk_id = v_res['chunk_id']
        company = v_res.get('company_name', 'Unknown')
        end_date = v_res.get('end_date', '')
        v_score = v_res['vector_score']
        
        g_res = graph_map.get(chk_id, {})
        edges = g_res.get('edges', [])
        total_edges = g_res.get('total_edges', 0)
        
        raw_graph_score = sum(ACTION_WEIGHTS.get(edge['action'], 1.0) for edge in edges)
        final_graph_score = math.log(max(raw_graph_score, 0) + 1)
        
        # Calculate Final Chunk Score
        recency_mult = calculate_recency_multiplier(end_date)
        
        # User Formula: Final_Chunk_Score = (Graph_Action_Weight * 0.6) + (Vector_Score * 0.3) + (Edge_Bonus)
        # Using final_graph_score for Graph_Action_Weight
        edge_bonus = min(total_edges * 0.01, 1.0) # Bonus capping
        final_chunk_score = ((final_graph_score * 0.6) + (v_score * 0.3) + edge_bonus) * recency_mult
        
        chunk_obj = {
            "chunk_id": chk_id,
            "company": company,
            "end_date": end_date,
            "recency_mult": recency_mult,
            "graph_score": final_graph_score,
            "vector_score": v_score,
            "final_score": final_chunk_score,
            "matched_edges": [e['skill'] for e in edges],
            "total_edges": total_edges
        }

        # Update candidate if this chunk is better
        if cid not in candidates_best_chunk:
            candidates_best_chunk[cid] = {"id": cid, "name": v_res['name'], "best_chunk": chunk_obj}
        elif final_chunk_score > candidates_best_chunk[cid]["best_chunk"]["final_score"]:
            candidates_best_chunk[cid]["best_chunk"] = chunk_obj

    # Sort Candidates by their Best Chunk's Final Score
    sorted_results = sorted(
        candidates_best_chunk.values(),
        key=lambda x: (x["best_chunk"]["final_score"], x["best_chunk"]["vector_score"]),
        reverse=True
    )
    
    # Format to traditional API response
    final_output = []
    for cand in sorted_results[:10]:
        best = cand["best_chunk"]
        
        # UX Explainability String
        explain = f"[{best['company']}]에서 최근 역량 인정 ({best['end_date']} 종료). "
        if best["recency_mult"] > 1.0: explain += "(최신경력 부스팅 적용🚀)"
        elif best["recency_mult"] < 1.0: explain += "(과거경력 패널티⬇️)"
        
        final_output.append({
            "name": cand["name"],
            "hash": cand["id"],
            "score": best["final_score"],
            "best_company": best["company"],
            "explain_reason": explain,
            "graph_score": best["graph_score"],
            "vector_score": best["vector_score"],
            "matched_edges": best["matched_edges"],
            "total_edges": best["total_edges"],
            "raw_text": "",
            "summary": "V9.0 Chunk-level Evaluated."
        })
        
    return final_output
"""

with open("jd_compiler.py", "r", encoding="utf-8") as f:
    text = f.read()

# Remove the old api_search_v9 and inject the new one
text = re.sub(r'def api_search_v9\(.*?\n\s+return final_output\n', '', text, flags=re.DOTALL)
text += "\n" + v9_advanced_code

with open("jd_compiler.py", "w", encoding="utf-8") as f:
    f.write(text)

print("V9 Chunk-Level API PATCH APPLIED!")
