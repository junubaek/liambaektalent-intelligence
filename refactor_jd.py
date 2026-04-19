import re

def rewrite_jd_compiler():
    with open('jd_compiler.py', 'r', encoding='utf-8') as f:
        content = f.read()

    # 1. calculate_gravity_fusion_score function signature and early return
    c1_old = """def calculate_gravity_fusion_score(candidate_edges, target_node, graph_score, vector_score):

    # 1. 타겟 노드가 없거나 엣지가 정상적인 리스트가 아닐 때의 기본 점수 방어

    if not target_node or not isinstance(candidate_edges, list):

        return (math.log(max(graph_score, 0) + 1) * 0.6) + (vector_score * 0.4)"""
    
    c1_new = """def calculate_gravity_fusion_score(candidate_edges, target_node, graph_score, vector_score=0.0):

    # 1. 타겟 노드가 없거나 엣지가 정상적인 리스트가 아닐 때의 기본 점수 방어

    if not target_node or not isinstance(candidate_edges, list):

        return math.log(max(graph_score, 0) + 1)"""
        
    content = content.replace(c1_old, c1_new)

    # 2. calculate_gravity_fusion_score base_score
    c2_old = "base_score = (math.log(max(adjusted_graph_score, 0) + 1) * 0.6) + (vector_score * 0.4)"
    c2_new = "base_score = math.log(max(adjusted_graph_score, 0) + 1)"
    content = content.replace(c2_old, c2_new)

    # 3. prefilter_candidates_by_tfidf removal
    # We will use Regex to remove the function block entirely.
    pattern_tfidf = r"def prefilter_candidates_by_tfidf(.*?)return \[\{'name': c\['name'\], 'vector_score': c\['sim'\], 'graph_score': 0\.0\} for c in top_cands\]"
    content = re.sub(pattern_tfidf, "", content, flags=re.DOTALL)

    # 4. Fallback replacement
    fb_old = """    # 2. 안전망 (Fallback) 가동
    min_fallback = 50
    if len(top_names) < min_fallback:
        logger.warning(f"⚠️ Graph 검색 결과 부족 ({len(top_names)}명). TF-IDF Fallback 즉시 가동...")
        needed_count = num_candidates - len(top_names)
        
        try:
            fallback_results = prefilter_candidates_by_tfidf(jd_text, num_candidates=needed_count)
            # 기존 결과에 TF-IDF 결과 병합 (중복 제거)
            seen = set([item['name'] for item in top_names])
            for item in fallback_results:
                if item['name'] not in seen:
                    top_names.append(item)
                    seen.add(item['name'])
        except Exception as e:
            logger.error(f"⚠️ TF-IDF Fallback 실패: {e}")"""

    fb_new = """    # 2. 안전망 (Fallback) 가동: Graph 0명일 때만 SQLite LIKE 검색
    if len(top_names) == 0:
        logger.warning(f"⚠️ Graph 검색 결과 0명. SQLite 원문 단순 LIKE 검색 Fallback 즉시 가동...")
        query_words = []
        if extracted_conditions:
            for c in extracted_conditions:
                if c.get("skill"):
                    # 단어가 여러 개인 경우 (예: "vLLM PyTorch") 쪼개서 넣기
                    words = c["skill"].lower().split()
                    query_words.extend(words)
        else:
            query_words = jd_text.lower().split()
            
        import sqlite3
        try:
            conn = sqlite3.connect('candidates.db')
            c = conn.cursor()
            
            # AND 검색
            where_clauses = []
            params = []
            for word in query_words:
                where_clauses.append("LOWER(raw_text) LIKE ?")
                params.append(f"%{word}%")
            
            if where_clauses:
                query = f"SELECT name_kr FROM candidates WHERE {' AND '.join(where_clauses)} LIMIT {num_candidates}"
                c.execute(query, params)
                fallback_rows = c.fetchall()
                
                # OR 검색 (AND 검색 결과가 0명이고 키워드가 여러개일 경우)
                if len(fallback_rows) == 0 and len(query_words) > 1:
                    logger.warning("SQLite AND 검색 0명. OR 조건으로 재검색합니다.")
                    where_clauses_or = []
                    params_or = []
                    for word in query_words:
                        where_clauses_or.append("LOWER(raw_text) LIKE ?")
                        params_or.append(f"%{word}%")
                    query_or = f"SELECT name_kr FROM candidates WHERE {' OR '.join(where_clauses_or)} LIMIT {num_candidates}"
                    c.execute(query_or, params_or)
                    fallback_rows = c.fetchall()
                    
                seen = set([item['name'] for item in top_names])
                for cand in fallback_rows:
                    if cand[0] not in seen:
                        top_names.append({'name': cand[0], 'graph_score': 0.0, 'vector_score': 0.0})
                        seen.add(cand[0])
                        
            conn.close()
            logger.info(f"✅ SQLite Fallback으로 통과자 추가됨. 현재 top_names 길이: {len(top_names)}")
        except Exception as e:
            logger.error(f"⚠️ SQLite Fallback 실패: {e}")"""
            
    content = content.replace(fb_old, fb_new)
    
    # 5. Tie-breaking sorting logic
    s1_old = "final_results.append({'candidate_id': name, 'name_kr': name, 'name': name, 'score': round(real_score, 2)})"
    s1_new = "final_results.append({'candidate_id': name, 'name_kr': name, 'name': name, 'score': round(real_score, 2), 'total_edges': len(cand_edges)})"
    content = content.replace(s1_old, s1_new)
    
    s2_old = "final_results.sort(key=lambda x: x['score'], reverse=True)"
    s2_new = "final_results.sort(key=lambda x: (x['score'], x['total_edges']), reverse=True)"
    content = content.replace(s2_old, s2_new)

    with open('jd_compiler.py', 'w', encoding='utf-8') as f:
        f.write(content)
        
    print("ALL REPLACEMENTS COMPLETED!")

if __name__ == '__main__':
    rewrite_jd_compiler()
