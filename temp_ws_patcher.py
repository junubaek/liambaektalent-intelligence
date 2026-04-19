import sys
import os
import re

ROOT_DIR = r"c:\Users\cazam\Downloads\이력서자동분석검색시스템"
jd_path = os.path.join(ROOT_DIR, "jd_compiler.py")

with open(jd_path, "r", encoding="utf-8") as f:
    text = f.read()

# Update Phase 1 and Phase 2 limits
text = re.sub(r"CALL db\.index\.vector\.queryNodes\('candidate_embedding', \d+, \$queryVector\)", 
              f"CALL db.index.vector.queryNodes('candidate_embedding', 75, $queryVector)", text)
                 
text = re.sub(r"graph_results = graph_candidates\[:\d+\]", 
              f"graph_results = graph_candidates[:50]", text)

prefix_marker = '    # [Phase 3: RRF Fusion]'
end_marker = "return {'matched'"

idx1 = text.find(prefix_marker)
idx2 = text.find(end_marker, idx1)
end_idx = text.find('\n', idx2)
if end_idx == -1: end_idx = len(text)

text_before = text[:idx1]
text_after = text[end_idx:]

new_fusion = """    # [Phase 3: Weighted Sum Fusion (Two-Tower)]
    combined_ids = list(set([c['id'] for c in vector_results] + [c['id'] for c in graph_results]))
    
    if not combined_ids:
        driver.close()
        return {'matched': [], 'total': 0, "is_category_search": is_category_search}
        
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
    
    for cid in combined_ids:
        name = id_to_name.get(cid, cid)
        c_info = cache_map.get(cid) or cache_map.get(name) or {}
        sectors = c_info.get("main_sectors", [])
        
        cand_edges = edges_map.get(cid, [])
        matched_str_list = [f"{e['action']}:{e['skill']}" for e in cand_edges]
        
        v_score = vscore_map.get(cid, 0.0)
        
        raw_g = calculate_gravity_fusion_score(cand_edges, conds, is_category_search)
        g_score = math.log(max(raw_g, 0) + 1)
        
        final_score = (v_score * 0.6) + (g_score * 0.4)
            
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
            'ws_score': final_score,
            '_score': final_score,
            'graph_score': round(g_score, 4),
            'vector_score': round(v_score, 4),
            'total_edges': len(cand_edges)
        }
        
        a_cnt = Counter(e['action'] for e in cand_edges)
        s_cnt = Counter(e['skill'] for e in cand_edges)
        payload['top_actions'] = [f"{k}({v})" for k,v in a_cnt.most_common(3)]
        payload['top_skills'] = [f"{k}({v})" for k,v in s_cnt.most_common(3)]
        
        final_results.append(payload)

    if not final_results:
        return {'matched': [], 'total': 0, "is_category_search": is_category_search}

    max_final = max([r['ws_score'] for r in final_results]) if final_results else 1.0
    if max_final <= 0: max_final = 1.0
    
    for r in final_results:
        norm_score = (r['ws_score'] / max_final) * 100
        r['score'] = round(norm_score, 4)
        r['_score'] = round(norm_score, 4)
        r['ws_score'] = round(r['ws_score'], 6)

    final_results.sort(key=lambda x: (-x['ws_score'], -x['total_edges']))
    
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
            best = max(cluster, key=lambda x: x['ws_score'])
            dedup.append(best)
            
    dedup.sort(key=lambda x: (-x['ws_score'], -x['total_edges']))
    
    return {'matched': dedup[:10], 'total': len(dedup), "is_category_search": is_category_search}"""

new_text = text_before + new_fusion + text_after

with open(jd_path, "w", encoding="utf-8") as f:
    f.write(new_text)

print("WS Patch applied.")
