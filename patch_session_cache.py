import re

patch_script = """
import uuid

SESSION_STORE = {}

def update_session(session_id, top_names, conds, min_years):
    SESSION_STORE[session_id] = {
        "top_names": top_names,
        "conditions": conds,
        "min_years": min_years
    }
"""

with open("jd_compiler.py", "r", encoding="utf-8") as f:
    code = f.read()

# 1. Insert SESSION_STORE at the top
if "SESSION_STORE =" not in code:
    code = code.replace("import json", "import json\nimport uuid\n\nSESSION_STORE = {}", 1)

# 2. Rewrite run_jd_compiler
new_run_jd_compiler = """def run_jd_compiler(jd_text: str, session_id: str = None, refine_text: str = None, skills_to_add: list = None, skills_to_remove: list = None, refined_min_years: int = None):
    import time
    start_time = time.time()
    
    print("=" * 60)
    print(f"[JD Compiler] Input: {jd_text} / Session: {session_id}")
    print("=" * 60)

    is_refine = session_id and session_id in SESSION_STORE

    if is_refine:
        print("\\n⚡ [SESSION CACHE HIT] Refine Mode Triggered! ⚡")
        cached = SESSION_STORE[session_id]
        top_names = cached["top_names"]
        conds = list(cached["conditions"])  # deep copy approx
        min_years = cached["min_years"] if refined_min_years is None else refined_min_years
        
        # Mode B: 구조화 수정 (Gemini 0회)
        if skills_to_remove:
            conds = [c for c in conds if c["skill"] not in skills_to_remove]
        if skills_to_add:
            for s in skills_to_add:
                conds.append({"action": "BUILT", "skill": s, "weight": 1.0, "is_mandatory": False})
                
        # Mode A: 자연어 수정 (Gemini 1회 호출)
        if refine_text:
            delta = parse_jd_to_json(refine_text)
            delta_conds = delta.get("conditions", [])
            if delta.get("min_years"):
                min_years = delta.get("min_years")
            # 다운그레이드 처리 후 원본 array에 합치기
            delta_conds = apply_downgrade_map(delta_conds)
            conds.extend(delta_conds)
            
        print(f"\\n[Refined Conditions] (Min Years: {min_years})")
        print(json.dumps(conds, indent=2, ensure_ascii=False))
        
        # Phase 1.5 Auto-Affinity Re-injection
        conds = inject_node_affinity(conds)
        affinity_conds = [c for c in conds if c.get("source") == "auto_affinity"]
        
        # TF-IDF 생략, 바로 Neo4j 재계산 (Phase 3)
        print("\\n[Phase 3] Executing Neo4j OPTIONAL MATCH Score calculation...")
    else:
        # Phase 1: Gemini 의도 추출
        extracted = parse_jd_to_json(jd_text)
        conds = extracted.get("conditions", [])
        min_years = extracted.get("min_years", 0)
        
        conds = apply_downgrade_map(conds)
        extracted["conditions"] = conds
        
        print("\\n[Phase 1] Extracted Conditions:")
        print(json.dumps(extracted, indent=2, ensure_ascii=False))

        if not conds:
            print("조건을 추출하지 못했습니다.")
            return

        conds = inject_node_affinity(conds)
        affinity_conds = [c for c in conds if c.get("source") == "auto_affinity"]
        if affinity_conds:
            print(f"\\n[Phase 1.5] Auto-Affinity Injected ({len(affinity_conds)}개):")
            for c in affinity_conds:
                print(f"  + {c['action']}:{c['skill']} (w:{c['weight']})")

        # Phase 2: TF-IDF 벡터 선추출
        print("\\n[Phase 2] Executing Vector Prefilter (TF-IDF)...")
        top_names = prefilter_candidates(jd_text, num_candidates=300)
        
        # 세션 발급
        session_id = str(uuid.uuid4())
        SESSION_STORE[session_id] = {
            "top_names": top_names,
            "conditions": conds,
            "min_years": min_years
        }
        print(f"\\n[Session] 발급됨: {session_id}")

        # Phase 3: Neo4j OPTIONAL MATCH 스코어링
        print(f"\\n[Phase 3] Executing Neo4j OPTIONAL MATCH Score calculation (min_years={min_years})...")

    # 공통 Phase 3 실행
    results = opt_match_score(top_names, conds, min_years=min_years)

    # 3.5. History 가산점 부여
    history_bonuses = get_history_bonus_scores(jd_text)
    for c in results:
        for b_name, b_val in history_bonuses.items():
            if b_name and b_name in c['name']:
                c['total_score'] = round(c['total_score'] + b_val['score'], 2)
                c['history_msg'] = b_val['msg']
                break

    results.sort(key=lambda x: x['total_score'], reverse=True)

    end_time = time.time()
    
    print("\\n" + "=" * 60)
    print(f"🏆 [FINAL RANKED CANDIDATES] (Top 20 | Pass Hurdle: 40%) | Elapsed: {end_time - start_time:.3f}s")
    print("=" * 60)
    print(f"➡️  Current Session ID: {session_id}\\n")

    if not results:
        print("조건(40%)을 만족하는 최종 합격 후보자가 없습니다.")
        return session_id

    # affinity_conds calculation for highlighting
    affinity_conds = [c for c in conds if c.get("source") == "auto_affinity"]
    for rank, c in enumerate(results[:20], start=1):
        auto_hits = [
            e for e in c.get("matched_edges", [])
            if any(a["skill"] in e for a in affinity_conds)
        ]
        print(f"{rank}. {c['name']} | Total Score: {c['total_score']}")
        if c.get("history_msg"):
            print(f"   {c['history_msg']}")
        print(f"   [+] Matched: {c['matched_edges']}")
        if auto_hits:
            print(f"   [~] Auto-Affinity Hit: {auto_hits}")
        if c.get("missing_edges"):
            print(f"   [-] Missing (for interview): {c['missing_edges']}")
        print("-" * 40)
        
    return session_id
"""

old_run_jd_pattern = r"def run_jd_compiler\(jd_text:\s*str\):.*?(?=def api_search_v8)"
code = re.sub(old_run_jd_pattern, new_run_jd_compiler + "\n\n", code, flags=re.DOTALL)

with open("jd_compiler.py", "w", encoding="utf-8") as f:
    f.write(code)

print("Patching jd_compiler.py completed.")
