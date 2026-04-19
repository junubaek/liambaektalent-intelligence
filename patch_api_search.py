import re

with open("jd_compiler.py", "r", encoding="utf-8") as f:
    code = f.read()

new_api_search = """def api_search_v8(prompt: str, sectors: list = None, seniority: str = "All", required: list = None, preferred: list = None, session_id: str = None, refine_text: str = None, skills_to_add: list = None, skills_to_remove: list = None, refined_min_years: int = None):
    \"\"\"
    FastAPI 엔드포인트용 V8 Wrapper.
    \"\"\"
    import time
    start_time = time.time()
    logger.info(f"[V8 API Search] Payload: {prompt} / Session: {session_id}")
    
    is_refine = session_id and session_id in SESSION_STORE
    
    if is_refine:
        logger.info(f"[Phase 1] ⚡ Session CACHE HIT! Refine Mode.")
        cached = SESSION_STORE[session_id]
        top_names = cached["top_names"]
        conds = list(cached["conditions"])
        min_years = cached["min_years"] if refined_min_years is None else refined_min_years
        
        # Mode B
        if skills_to_remove:
            conds = [c for c in conds if c["skill"] not in skills_to_remove]
        if skills_to_add:
            for s in skills_to_add:
                conds.append({"action": "BUILT", "skill": s, "weight": 1.0, "is_mandatory": False})
                
        # Mode A
        if refine_text:
            delta = parse_jd_to_json(refine_text)
            delta_conds = delta.get("conditions", [])
            if delta.get("min_years"):
                min_years = delta.get("min_years")
            delta_conds = apply_downgrade_map(delta_conds)
            conds.extend(delta_conds)
            
        conds = inject_node_affinity(conds)
        
    else:
        # 1. 의도 추출 (Gemini)
        extracted = parse_jd_to_json(prompt)
        conds = extracted.get("conditions", [])
        min_years = extracted.get("min_years", 0)
        
        # 1-1. 다운그레이드 매핑 적용
        conds = apply_downgrade_map(conds)
        conds = inject_node_affinity(conds)
        
        if not conds:
            return {"matched": [], "nearby": [], "alternative": None, "gap_flags": [], "db_miss_risk": [], "total": 0, "parsed": {}, "session_id": None}
            
        # 2. 벡터 선추출 (TF-IDF)
        top_names = prefilter_candidates(prompt, num_candidates=300)
        
        # 세션 캐시 저장
        import uuid
        session_id = str(uuid.uuid4())
        SESSION_STORE[session_id] = {
            "top_names": top_names,
            "conditions": conds,
            "min_years": min_years
        }

    # 3. Neo4j Scoring (Phase 3)
    results = opt_match_score(top_names, conds, min_years=min_years)
    
    # 3.5. History 가산점 부여
    history_bonuses = get_history_bonus_scores(prompt if not is_refine else refine_text or prompt)
    for c in results:
        for b_name, b_val in history_bonuses.items():
            if b_name and b_name in c['name']:
                c['total_score'] = round(c['total_score'] + b_val['score'], 2)
                c['history_msg'] = b_val['msg']
                break
            
    # 재정렬
    results.sort(key=lambda x: x['total_score'], reverse=True)
    
    # 4. 프론트엔드 포맷팅 (Matched)
    candidates = get_candidates_from_notion()
    cand_map = {c['name']: c for c in candidates}
    matched = []
    
    for r in results:
        r_name = r["name"]
        raw_c = cand_map.get(r_name, {})
        
        matched_str = " | ".join(r["matched_edges"]) if r["matched_edges"] else "None"
        missing_str = " | ".join(r["missing_edges"]) if r["missing_edges"] else "전체 조건 충족"
        mech_text = f"[+] Matched: {matched_str}<br>[-] Missing: {missing_str}"
        if r.get("history_msg"):
            mech_text += f"<br><b>{r['history_msg']}</b>"
        
        sub_sectors_val = raw_c.get("sub_sectors", [])
        if not isinstance(sub_sectors_val, list):
            sub_sectors_val = []

        ui_cand = {
            "id": raw_c.get("id", ""),
            "notion_url": raw_c.get("notion_url", "#"),
            "이름": r_name,
            "Main Sectors": raw_c.get("main_sectors", []),
            "Sub Sectors": sorted(list(set([cond['skill'] for cond in conds[:3]] + sub_sectors_val))),
            "연차등급": raw_c.get("seniority", "확인 요망"),
            "Experience Summary": raw_c.get("summary", ""),
            "_score": r["total_score"],
            "_mechanics": mech_text,
            "_gap_flags": []
        }
        matched.append(ui_cand)
    
    logger.info(f"[V8 API Search] Elapsed: {time.time()-start_time:.3f}s / Total Hits: {len(matched)}")
    
    return {
        "matched": matched[:20],
        "nearby": [],
        "alternative": None,
        "gap_flags": [],
        "db_miss_risk": [],
        "total": len(matched),
        "parsed": {},
        "session_id": session_id
    }
"""

old_api_pattern = r"def api_search_v8\(.*(?=\n\nif __name__ ==)"
# The above pattern won't work well due to .*
# Better slice by 'def api_search_v8' and 'if __name__ == "__main__":'
parts = code.split('def api_search_v8(')
if len(parts) > 1:
    tail_parts = parts[1].split('if __name__ == "__main__":')
    if len(tail_parts) > 1:
        new_code = parts[0] + new_api_search + '\n\nif __name__ == "__main__":' + tail_parts[1]
        with open("jd_compiler.py", "w", encoding="utf-8") as f:
            f.write(new_code)
        print("api_search_v8 patched successfully.")
    else:
        print("Failed to find main block")
else:
    print("Failed to find api_search_v8")
