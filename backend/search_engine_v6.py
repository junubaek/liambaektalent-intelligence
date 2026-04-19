import os
from typing import List
import json
import re

from app.graph_engine.core_graph import SkillGraphEngine
from app.graph_engine.obsidian_parser import ObsidianParser
from app.engine.resume_snap import CandidateSnapper
from app.engine.neo4j_snapper import Neo4jCandidateSnapper

# V5 Modules (for Text Search)
from backend.search_engine_v5 import gemini_parse_prompt, build_notion_filter, notion_query_raw, expand_query

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VAULT_DIR = os.path.join(ROOT_DIR, "obsidian_vault")

# 1. 인메모리 Graph 매핑 엔진 부트스트랩
print("[V6] Bootstrapping Memory Alias Graph for fast text-to-node routing...")
parser = ObsidianParser(VAULT_DIR)
parsed_nodes = parser.parse_all_nodes()
graph_engine = SkillGraphEngine()
graph_engine.build_graph(parsed_nodes)
snapper = CandidateSnapper(graph_engine)

def search_candidates_v6(prompt: str, sectors: List[str], seniority: str, required: List[str], preferred: List[str]):
    print(f"\n[V6 Search] Request: {prompt}, req: {required}, pref: {preferred}")
    
    # -----------------------------------------------------
    # Phase 1: NLP / Semantic Text Filter (Notion DB)
    # -----------------------------------------------------
    parsed = gemini_parse_prompt(prompt) if prompt.strip() else {}
    
    required_groups  = [expand_query(kw) for kw in required]
    preferred_groups = [expand_query(kw) for kw in preferred]
    pattern_groups   = [expand_query(kw) for kw in parsed.get("pattern_keywords", [])]
    
    all_terms = (
        [t for g in required_groups  for t in g] +
        [t for g in preferred_groups for t in g] +
        [t for g in pattern_groups   for t in g]
    )
    
    f = build_notion_filter(
        main_sectors = sectors,
        sub_sectors  = parsed.get("sub_sectors", []),
        search_terms = all_terms,
        seniority    = seniority,
        exclude      = parsed.get("exclude", []),
    )
    
    candidate_ids = None
    notion_map = {}
    
    # 필터가 존재하면 1차적으로 텍스트 매칭을 통과한 인원만 추린다
    if f or all_terms or parsed.get("sub_sectors"):
        print(f"[V6.1] Running Notion Native Search for unstructured text... {all_terms}")
        raw_candidates = notion_query_raw(f, page_size=150)
        candidate_ids = [c["id"] for c in raw_candidates]
        notion_map = {c["id"]: c for c in raw_candidates}
        print(f"[V6.1] Passed Text Filter: {len(candidate_ids)} candidates.")
        
        if not candidate_ids:
            return {
                "matched": [], "nearby": [], "alternative": None,
                "gap_flags": parsed.get("gap_flags", []), "db_miss_risk": parsed.get("db_miss_risk", []),
                "total": 0, "parsed": parsed
            }

    # -----------------------------------------------------
    # Phase 2: Graph Node Extraction & Tendency
    # -----------------------------------------------------
    # 모든 추출된 키워드(Required, Preferred, Sub_Sectors 등)를 종합하여 Graph Node 매핑
    extraction_input_req = required + parsed.get("sub_sectors", [])
    extraction_input_pref = preferred + parsed.get("pattern_keywords", [])
    
    required_nodes = snapper.extract_and_map_skills(extraction_input_req)
    preferred_nodes = snapper.extract_and_map_skills(extraction_input_pref)
    prompt_nodes = snapper.extract_and_map_skills([prompt])
    exclude_nodes = snapper.extract_and_map_skills(parsed.get("exclude", []))
    
    combined_nodes = {}
    
    for node, w in required_nodes.items():
        combined_nodes[node] = {"weight": max(4.0, combined_nodes.get(node, {}).get("weight", 0)), "is_core": True}
    for node, w in preferred_nodes.items():
        combined_nodes[node] = {"weight": max(2.0, combined_nodes.get(node, {}).get("weight", 0)), "is_core": combined_nodes.get(node, {}).get("is_core", False)}
    for node, w in prompt_nodes.items():
        combined_nodes[node] = {"weight": max(1.0, combined_nodes.get(node, {}).get("weight", 0)), "is_core": combined_nodes.get(node, {}).get("is_core", False)}

    # Apply Negative Weights for Excluded Intent LAST, so it OVERWRITES any previously assigned positive weights
    for node, w in exclude_nodes.items():
        combined_nodes[node] = {"weight": -1.0, "is_core": False}
        
    jd_nodes_list = [{"name": name, "weight": info["weight"], "is_core": info["is_core"]} for name, info in combined_nodes.items()]
    
    # 추출 실패시 Fallback 노드는 부여하지 않음 (Text 매치로 잡혔는데 그래프 점수가 0이면 Nearby로 빠뜨리기 위해)
    # 다만 질량이 안 뽑히면 DB서칭 에러가 날 수 있으니 최소한의 노드 세팅
    if not jd_nodes_list:
        jd_nodes_list = [{"name": "영업", "weight": 1.0, "is_core": False}] # Dummy fallback

    raw_for_tendency = {n: i["weight"] for n, i in combined_nodes.items()}
    jd_tendency = snapper.get_tendency_vector(raw_for_tendency)
    
    # -----------------------------------------------------
    # Phase 3: Neo4j Gravity & Tendency Physics Equation
    # -----------------------------------------------------
    uri = "neo4j+ssc://2c78ff2f.databases.neo4j.io"
    user = "neo4j"
    password = "sUdocj6IJEdIWCPNE6qzJq7kCdynS6EjSuBeKJtcye4"
    neo_engine = Neo4jCandidateSnapper(uri, user, password)
    
    try:
        neo_results = neo_engine.search_candidates(jd_tendency, jd_nodes_list, candidate_ids=candidate_ids)
    finally:
        neo_engine.close()
        
    matched = []
    nearby = []
    
    for r in neo_results:
        f_score = r["final_score"]
        uuid_str = r['id'].replace('-', '')
        
        # Merge Notion Real Data with Neo4j DB Output
        notion_cand = notion_map.get(r["id"], {})
        
        secs = [s.strip() for s in r.get("sectors", "").split(",") if s.strip()]
        if not secs: secs = notion_cand.get("Main Sectors", ["미지정 Sector"])
            
        summary_text = notion_cand.get("Experience Summary", "요약 정보 없음")
        mech_text = f"중력(Gravity): {r['raw_gravity']:.2f}G | 경향성 일치율: {r['tendency_score'] * 100:.1f}%" if f_score > 0 else "텍스트 시맨틱 단독 매칭 (그래프 중력장 미진입)"
        
        ui_cand = {
            "id": r["id"],
            "notion_url": f"https://www.notion.so/{uuid_str}",
            "이름": r["name"] or notion_cand.get("이름", "Unknown"),
            "Main Sectors": secs,
            "Sub Sectors": sorted(list(set([node["name"] for node in jd_nodes_list[:3]] + notion_cand.get("Sub Sectors", [])))),
            "연차등급": notion_cand.get("Seniority Bucket", seniority if seniority != "All" else "확인 요망"),
            "Experience Summary": summary_text,
            "_score": round(f_score, 2),
            "_mechanics": mech_text,
            "_gap_flags": parsed.get("gap_flags", [])
        }
        
        # Hard Filter 기준점을 좀 더 느슨하게 변경 (Text Match를 통과했으므로)
        if f_score >= 0.1:
            matched.append(ui_cand)
        else:
            nearby.append(ui_cand)
            
    # 후보자가 Text를 통과했는데 Graph에 아예 매핑이 안되어 결과 배열에 없는 경우 (Graph Score 0)
    # fallback to manual Nearby Add
    processed_ids = {r["id"] for r in neo_results}
    if candidate_ids:
        for cid in candidate_ids:
            if cid not in processed_ids:
                nc = notion_map.get(cid)
                uuid_str = cid.replace('-', '')
                nearby.append({
                    "id": cid,
                    "notion_url": f"https://www.notion.so/{uuid_str}",
                    "이름": nc.get("이름", "Unknown"),
                    "Main Sectors": nc.get("Main Sectors", []),
                    "Sub Sectors": nc.get("Sub Sectors", []),
                    "연차등급": nc.get("Seniority Bucket", "확인 요망"),
                    "Experience Summary": nc.get("Experience Summary", "요약 정보 없음"),
                    "_score": 0.0,
                    "_mechanics": "텍스트 시맨틱 단독 매칭 (그래프 중력장 미진입)",
                    "_gap_flags": parsed.get("gap_flags", [])
                })
                
    # Sort
    matched.sort(key=lambda x: x["_score"], reverse=True)
    nearby.sort(key=lambda x: x["_score"], reverse=True)
    
    return {
        "matched": matched[:15],
        "nearby": nearby[:15],
        "alternative": None,
        "gap_flags": parsed.get("gap_flags", []),
        "db_miss_risk": parsed.get("db_miss_risk", []),
        "total": len(matched[:15]) + len(nearby[:15]),
        "parsed": parsed
    }
