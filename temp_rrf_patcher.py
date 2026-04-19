import sys
import os

ROOT_DIR = r"c:\Users\cazam\Downloads\이력서자동분석검색시스템"
jd_path = os.path.join(ROOT_DIR, "jd_compiler.py")

with open(jd_path, "r", encoding="utf-8") as f:
    text = f.read()

prefix_marker = '    # [Phase 1: Vector Search]'
if prefix_marker not in text:
    print("Prefix marker not found!")
    sys.exit(1)

# Find the end of the api_search_v8 function.
end_idx = text.find("return {'matched':", text.find(prefix_marker))
if end_idx == -1:
    print("Return line not found!")
    sys.exit(1)

# We need to find the newline right after the return statement
newline_idx = text.find('\n', end_idx)

text_before = text[:text.find(prefix_marker)]
text_after = text[newline_idx:]

new_logic = """    # [Phase 1: Vector Search (Tower 1)]
    emb_res = client.embeddings.create(input=[prompt], model="text-embedding-3-small")
    query_vector = emb_res.data[0].embedding
    
    vector_results = []
    id_to_name = {}
    
    driver = GraphDatabase.driver("bolt://127.0.0.1:7687", auth=("neo4j", "toss1234"))
    try:
        with driver.session() as session:
            q_vec = \"\"\"
            CALL db.index.vector.queryNodes('candidate_embedding', 75, $queryVector)
            YIELD node AS c, score
            RETURN c.id AS id, coalesce(c.name_kr, c.name) AS name, score
            \"\"\"
            res = session.run(q_vec, queryVector=query_vector)
            for r in res:
                cid = str(r["id"]) if r["id"] else r["name"]
                if cid:
                    vector_results.append({'id': cid, 'name': r['name'], 'score': r['score']})
                    id_to_name[cid] = r['name']
    except Exception as e:
        logger.error(f"[Tower 1] Vector error: {e}")
        
    logger.info(f"[Tower 1] Extracted Top-30 via Pinecone.")

    # [Phase 2: Graph Score (Tower 2)]
    target_skills = list(set([c.get("skill") for c in conds if c.get("skill")]))
    graph_candidates = []
    
    if target_skills:
        try:
            with driver.session() as session:
                q = \"\"\"
                MATCH (c:Candidate)-[r]->(s:Skill)
                WHERE s.name IN $target_skills AND type(r) <> 'USED_AS_TEMP' AND c.is_duplicate = 0
                WITH c, collect(DISTINCT {skill: s.name, action: type(r)}) AS skills
                RETURN coalesce(c.id, c.name_kr) AS id, coalesce(c.name_kr, c.name) AS name, skills
                \"\"\"
                res = session.run(q, target_skills=target_skills)
                for r in res:
                    cid = str(r["id"]) if r["id"] else r["name"]
                    cand_edges = r["skills"]
                    id_to_name[cid] = r['name']
                    
                    raw_graph_score = calculate_gravity_fusion_score(cand_edges, conds, is_category_search)
                    graph_score = math.log(max(raw_graph_score, 0) + 1)
                    
                    if graph_score > 0:
                        graph_candidates.append({
                            'id': cid,
                            'name': r['name'],
                            'graph_score': graph_score,
                            'cand_edges': cand_edges
                        })
                # Sort descending and take Top 30
                graph_candidates.sort(key=lambda x: x['graph_score'], reverse=True)
                graph_results = graph_candidates[:30]
                logger.info(f"[Tower 2] Graph Top-30 Evaluated.")
        except Exception as e:
            logger.error(f"[Tower 2] Graph error: {e}")
            graph_results = []
    else:
        graph_results = []
        logger.info(f"[Tower 2] No target skills to query graph.")

    # [Phase 3: RRF Fusion]
    scores = {}
    k = 60
    
    for rank, cand in enumerate(vector_results):
        cid = cand['id']
        scores[cid] = scores.get(cid, 0) + 1 / (k + rank + 1)
        
    for rank, cand in enumerate(graph_results):
        cid = cand['id']
        scores[cid] = scores.get(cid, 0) + 1 / (k + rank + 1)
        
    if not scores:
        driver.close()
        return {'matched': [], 'total': 0, "is_category_search": is_category_search}
        
    max_rrf = max(scores.values()) if scores else 1.0

    # Collect all needed edges for merged top candidates
    combined_ids = list(scores.keys())
    edges_map = {}
    try:
        with driver.session() as session:
            q_edge = \"\"\"
            MATCH (c:Candidate)-[r]->(s:Skill)
            WHERE (c.id IN $ids OR c.name_kr IN $ids) AND type(r) <> 'USED_AS_TEMP'
            RETURN coalesce(c.id, c.name_kr) AS id, collect(DISTINCT {skill: s.name, action: type(r)}) AS skills
            \"\"\"
            res_e = session.run(q_edge, ids=combined_ids)
            edges_map = {str(r["id"]): r["skills"] for r in res_e}
    except Exception as e:
        logger.error(f"Edges fetch error: {e}")
    finally:
        driver.close()

    vscore_map = {c['id']: c['score'] for c in vector_results}
    gscore_map = {c['id']: c['graph_score'] for c in graph_results}
    
    final_results = []
    from collections import Counter
    import math
    
    for cid, rrf_score in scores.items():
        name = id_to_name.get(cid, cid)
        c_info = cache_map.get(cid) or cache_map.get(name) or {}
        sectors = c_info.get("main_sectors", [])
        
        cand_edges = edges_map.get(cid, [])
        matched_str_list = [f"{e['action']}:{e['skill']}" for e in cand_edges]
        
        # 100-point scale normalization
        normalized_score = (rrf_score / max_rrf) * 100
        
        v_score = vscore_map.get(cid, 0.0)
        g_score = gscore_map.get(cid)
        if g_score is None:
            raw_g = calculate_gravity_fusion_score(cand_edges, conds, is_category_search)
            g_score = math.log(max(raw_g, 0) + 1)
            
        payload = {
            'id': cid,
            'candidate_id': cid,
            'name_kr': name,
            '이름': name,
            'current_company': c_info.get("current_company", "미상"),
            '연차등급': c_info.get("seniority", "확인 요망"),
            'sector': sectors[0] if sectors else "미분류",
            'Sub Sectors': sectors,
            'matched_edges': matched_str_list,
            'Experience Summary': c_info.get("summary", "정보 없음"),
            'profile_summary': c_info.get("profile_summary", ""),
            '연락처': c_info.get("phone", "번호 없음"),
            'email': c_info.get("email", "이메일 없음"),
            'birth_year': c_info.get("birth_year", "생년 미상"),
            'notion_url': c_info.get("notion_url", "#"),
            'google_drive_url': c_info.get("google_drive_url", None),
            'career': c_info.get("parsed_career_json") or c_info.get("careers", []),
            'education_json': c_info.get("education_json", []),
            'score': round(normalized_score, 4),
            '_score': round(normalized_score, 4),
            'rrf_score': round(rrf_score, 6),
            'graph_score': round(g_score, 4),
            'vector_score': round(v_score, 4),
            'total_edges': len(cand_edges)
        }
        
        a_cnt = Counter(e['action'] for e in cand_edges)
        s_cnt = Counter(e['skill'] for e in cand_edges)
        payload['top_actions'] = [f"{k}({v})" for k,v in a_cnt.most_common(3)]
        payload['top_skills'] = [f"{k}({v})" for k,v in s_cnt.most_common(3)]
        
        final_results.append(payload)

    final_results.sort(key=lambda x: (-x['_score'], -x['total_edges']))
    
    # Deduplication
    grouped_by_name = {}
    for r in final_results:
        if '무명' in r['name_kr']:
            grouped_by_name.setdefault(r['id'], []).append(r)
            continue
        import re
        pure_name = re.sub(r'[^가-힣a-zA-Z]', '', r['name_kr'])
        grouped_by_name.setdefault(pure_name, []).append(r)
        
    dedup = []
    for name_key, candidates_group in grouped_by_name.items():
        if '무명' in candidates_group[0]['name_kr'] or len(candidates_group) == 1:
            dedup.append(candidates_group[0])
            continue
            
        person_clusters = []
        for c in candidates_group:
            phone = c.get('phone', '').strip().replace('-', '') if c.get('phone') else ''
            company = c.get('current_company', '').strip() if c.get('current_company') else ''
            
            matched_cluster = None
            for p in person_clusters:
                p_phone = p[0].get('phone', '').strip().replace('-', '') if p[0].get('phone') else ''
                p_company = p[0].get('current_company', '').strip() if p[0].get('current_company') else ''
                
                if (phone and p_phone and phone == p_phone) or (company and p_company and company == p_company):
                    matched_cluster = p
                    break
            if matched_cluster is not None:
                matched_cluster.append(c)
            else:
                person_clusters.append([c])
                
        for cluster in person_clusters:
            best = max(cluster, key=lambda x: x['_score'])
            dedup.append(best)
            
    dedup.sort(key=lambda x: (-x['_score'], -x['total_edges']))
    
    return {'matched': dedup[:10], 'total': len(dedup), "is_category_search": is_category_search}"""

assembled_text = text_before + new_logic + text_after

with open(jd_path, "w", encoding="utf-8") as f:
    f.write(assembled_text)

print("Patch applied to jd_compiler.py!")
