import re
import os

def patch_backend():
    with open('jd_compiler.py', 'r', encoding='utf-8') as f:
        content = f.read()
        
    old_code = content[content.find('def api_search_v8'):content.find('def normalize_query_with_map')]

    new_code = """def api_search_v8(prompt: str, session_id: str = None, **kwargs) -> dict:
    import json
    import time
    import math
    from openai import OpenAI
    from neo4j import GraphDatabase
    
    st = time.time()
    logger.info(f"\\n\\n[V8 API Search] Payload: {prompt} / Session: {session_id}")
    
    # 1. Fetch Cache Map
    # Needs to be dynamically imported if inside
    from jd_compiler import get_candidates_from_cache
    cand_list = get_candidates_from_cache()
    # Map by id or name
    cache_map = {str(c.get('id', '')): c for c in cand_list}
    if not cache_map:
        # Fallback to mapping by name
        cache_map = {str(c.get('name_kr', '')): c for c in cand_list}

    extracted = parse_jd_to_json(prompt)
    conds = extracted.get("conditions", [])
    is_category_search = extracted.get("is_category_search", False)
    conds = deduplicate_conditions(conds)
    conds = apply_downgrade_map(conds)
    conds = inject_node_affinity(conds)
    
    with open("secrets.json", "r", encoding="utf-8") as f:
        secrets = json.load(f)
    api_key = secrets.get("OPENAI_API_KEY") or secrets.get("openai_api_key")
    
    client = OpenAI(api_key=api_key)
    
    # [Phase 1: Vector Search]
    emb_res = client.embeddings.create(input=[prompt], model="text-embedding-3-small")
    query_vector = emb_res.data[0].embedding
    
    top_150_vectors = {}
    top_ids = []
    id_to_name = {}
    
    driver = GraphDatabase.driver("bolt://127.0.0.1:7687", auth=("neo4j", "toss1234"))
    try:
        with driver.session() as session:
            q_vec = \"\"\"
            CALL db.index.vector.queryNodes('candidate_embedding', 150, $queryVector)
            YIELD node AS c, score
            RETURN c.id AS id, c.name_kr AS name, score
            \"\"\"
            res = session.run(q_vec, queryVector=query_vector)
            for r in res:
                cid = str(r["id"]) if r["id"] else r["name"]
                if cid:
                    top_150_vectors[cid] = r["score"]
                    top_ids.append(cid)
                    id_to_name[cid] = r["name"]
    except Exception as e:
        logger.error(f"[V8 API Search] Neo4j Vector error: {e}")
        return {'matched': []}
        
    if not top_ids:
        return {'matched': []}
        
    logger.info(f"[Phase 1] Extracted Top-150 via Neo4j Native Vector Index.")

    # [Phase 2: Graph Score]
    edges_map = {}
    try:
        with driver.session() as session:
            # Match by ID instead of name to avoid duplicates
            q = \"\"\"
            MATCH (c:Candidate)-[r]->(s:Skill)
            WHERE (c.id IN $ids OR c.name_kr IN $ids) AND type(r) <> 'USED_AS_TEMP' 
            RETURN coalesce(c.id, c.name_kr) AS id, collect(DISTINCT {skill: s.name, action: type(r)}) AS skills
            \"\"\"
            res = session.run(q, ids=top_ids)
            edges_map = {str(r["id"]): r["skills"] for r in res}
    except Exception as e:
        logger.error(f"[V8 API Search] Neo4j Graph error: {e}")
    finally:
        driver.close()

    final_results = []
    seen = set()
    
    for cid in top_ids:
        if cid in seen: continue
        seen.add(cid)
        
        name = id_to_name.get(cid, cid)
        v_score = top_150_vectors.get(cid, 0.0)
        cand_edges = edges_map.get(cid, [])
        
        # Calculate raw graph score
        raw_graph_score = calculate_gravity_fusion_score(cand_edges, conds, is_category_search)
        
        # Log smoothing
        graph_score = math.log(max(raw_graph_score, 0) + 1)
        
        # [Phase 3: Fusion]
        if is_category_search:
            final_score = (graph_score * 0.70) + (v_score * 0.30)
        else:
            final_score = (graph_score * 0.85) + (v_score * 0.15)
            
        c_info = cache_map.get(cid) or cache_map.get(name) or {}
        
        sectors = c_info.get("main_sectors", [])
        matched_str_list = [f"{e['action']}:{e['skill']}" for e in cand_edges]
        
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
            '이메일': c_info.get("email", "이메일 없음"),
            'notion_url': "#", # Can map real url if needed
            'career': c_info.get("careers", []),
            'education_json': c_info.get("education_json", []),
            'score': round(final_score, 4),
            '_score': round(final_score, 4),
            'graph_score': round(graph_score, 4),
            'vector_score': round(v_score, 4),
            'total_edges': len(cand_edges)
        }
        final_results.append(payload)
        
    final_results.sort(key=lambda x: (x['_score'], x['total_edges']), reverse=True)
    return {'matched': final_results, 'total': len(final_results)}

"""
    content = content.replace(old_code, new_code)
    with open('jd_compiler.py', 'w', encoding='utf-8') as f:
        f.write(content)


def patch_frontend():
    with open('script_3.js', 'r', encoding='utf-8') as f:
        js = f.read()

    # 1. Main Sector under Current / Latest
    old_header = '<p class="text-[12px] text-slate-500 font-bold tracking-tight"><span class="text-slate-400 mr-1.5 uppercase text-[9px]">Current / Latest :</span> ${company}</p>'
    new_header = '''<p class="text-[12px] text-slate-500 font-bold tracking-tight"><span class="text-slate-400 mr-1.5 uppercase text-[9px]">Current / Latest :</span> ${company}</p>
                                            <p class="text-[12px] text-slate-500 font-bold tracking-tight mt-0.5"><span class="text-slate-400 mr-1.5 uppercase text-[9px]">Main Sector :</span> ${sectorVal}</p>'''
    if old_header in js:
        js = js.replace(old_header, new_header)

    # 2. Graph / Vector Scores rendering
    old_grid = '''<div class="grid grid-cols-1 md:grid-cols-3 gap-6 text-[11px] font-black uppercase tracking-tighter">
                                                <div class="flex flex-col gap-1.5">
                                                    <span class="text-slate-400 text-[9px]">Graph Path</span>
                                                    <span class="text-slate-800 leading-snug">${pathWithTags}</span>
                                                </div>
                                                <div class="flex flex-col gap-1.5 border-l border-slate-100 pl-6">
                                                    <span class="text-slate-400 text-[9px]">Match Edge</span>
                                                    <span class="text-slate-800 leading-snug">${matchedEdges.join(', ')}</span>
                                                </div>
                                                <div class="flex flex-col gap-1.5 border-l border-slate-100 pl-6">
                                                    <span class="text-slate-400 text-[9px]">Node Score</span>
                                                    <span class="text-black text-lg font-black">${score} <span class="text-slate-300 font-medium ml-1">/ 100</span></span>
                                                </div>
                                            </div>'''
                                            
    new_grid = '''<div class="grid grid-cols-10 gap-4 text-[11px] font-black uppercase tracking-tighter items-center">
                                                <div class="col-span-4 flex flex-col gap-1.5 pl-2">
                                                    <span class="text-slate-400 text-[9px]">Matched Nodes</span>
                                                    <span class="text-slate-800 leading-snug" style="font-size: 0.85rem; font-weight: 700; word-break: break-all;">${matchedEdges.join(', ')}</span>
                                                </div>
                                                <div class="col-span-3 flex flex-col gap-1.5 border-l border-slate-100 pl-6">
                                                    <span class="text-slate-400 text-[9px]">Graph Score</span>
                                                    <span class="text-indigo-600 text-[1.1rem] font-black">${c.graph_score || 0}</span>
                                                </div>
                                                <div class="col-span-3 flex flex-col gap-1.5 border-l border-slate-100 pl-6">
                                                    <span class="text-slate-400 text-[9px]">Vector Score</span>
                                                    <span class="text-blue-600 text-[1.1rem] font-black">${c.vector_score || 0}</span>
                                                </div>
                                            </div>'''
    if old_grid in js:
        js = js.replace(old_grid, new_grid)

    # 3. Evidence Summary (Education addition)
    old_evd = '''<div class="flex flex-col gap-4 pt-10 border-t border-slate-100">
                                                        <div class="flex gap-5 items-start">
                                                            <span class="text-[14px] font-black text-slate-800 shrink-0 mt-0.5">② 경력 상세 이력</span>'''
    
    new_evd = '''<div class="flex flex-col gap-4 pt-10 border-t border-slate-100">
                                                        <div class="flex gap-5 items-start">
                                                            <span class="text-[14px] font-black text-slate-800 shrink-0 mt-0.5">② 경력 상세 이력</span>'''
    if old_evd in js:
        js = js.replace(old_evd, new_evd)
        
    old_evd_tail = '''</div>
                                                            </div>
                                                        </div>
                                                    </div>'''
    
    new_evd_tail = '''</div>
                                                            </div>
                                                        </div>
                                                        <div class="flex gap-5 items-start pt-10 mt-6 border-t border-slate-100">
                                                            <span class="text-[14px] font-black text-slate-800 shrink-0 mt-0.5">③ 학력</span>
                                                            <div class="space-y-4 flex-1 text-[13.5px] font-medium text-slate-700">
                                                                ${(c.education_json && c.education_json.length > 0) ? c.education_json.map(edu => 
                                                                    `<div class="flex items-center justify-between border-b border-slate-50 border-dotted py-2 last:border-0">
                                                                        <p><span class="font-bold text-black">${edu.schoolName}</span>, ${edu.major} <span class="text-slate-400 ml-1">(${edu.degree})</span></p>
                                                                    </div>`
                                                                ).join('') : '<p class="text-slate-400 italic">등록된 학력 정보 없음</p>'}
                                                            </div>
                                                        </div>
                                                    </div>'''
                                                    
    if old_evd_tail in js:
        # replace the last occurrence to not break the DOM structure
        idx = js.rfind(old_evd_tail)
        if idx != -1:
            js = js[:idx] + new_evd_tail + js[idx+len(old_evd_tail):]
            
    with open('script_3.js', 'w', encoding='utf-8') as f:
        f.write(js)

if __name__ == '__main__':
    patch_backend()
    patch_frontend()
    print("Patch OK")
