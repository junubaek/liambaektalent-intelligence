
import os

code_to_append = """
def api_search_v9(prompt: str, session_id: str = None, **kwargs) -> dict:
    \"\"\"
    [Hybrid Search v9]
    Tower 1: Vector (Neo4j) - 40%
    Tower 2: Graph (Neo4j) - 30%
    Tower 3: BM25 (Local) - 30%
    \"\"\"
    import json, time, math
    from openai import OpenAI
    from neo4j import GraphDatabase
    
    st = time.time()
    logger.info(f\"\\n\\n[V9 Hybrid Search] Payload: {prompt} / Session: {session_id}\")
    
    # 0. Load Cache Maps
    from jd_compiler import get_candidates_from_cache
    cand_list = get_candidates_from_cache()
    cache_map = {str(c.get('id', '')): c for c in cand_list}
    
    # 1. Parse & Expand Query
    extracted = parse_jd_to_json(prompt)
    conds = extracted.get(\"conditions\", [])
    
    # Map abbreviations
    def map_abbreviations_to_conds(query_str, conditions_list):
        expansion_map = {
            \"IPO\": [\"Investor_Relations\", \"IPO_Preparation\"],
            \"IR\": [\"Investor_Relations\"],
            \"DFT\": [\"Design_for_Testability\"],
            \"RTL\": [\"RTL_Design\"],
            \"SoC\": [\"System_on_Chip\"],
            \"SAP\": [\"SAP_ERP\"],
            \"BI\": [\"Business_Intelligence\"],
            \"Tableau\": [\"Tableau\"],
            \"DevOps\": [\"DevOps\", \"CI_CD\"],
            \"SaaS\": [\"SaaS\"],
            \"Kotlin\": [\"Kotlin\", \"Android_Development\"],
            \"ASRS\": [\"Warehouse_Automation\"]
        }
        import re
        for abbr, expansions in expansion_map.items():
            if re.search(r'\\b' + re.escape(abbr) + r'\\b', query_str, re.IGNORECASE):
                for exp in expansions:
                    if not any(c.get('skill') == exp for c in conditions_list):
                        conditions_list.append({\"action\": \"MANAGED\", \"skill\": exp, \"is_mandatory\": False, \"source\": \"abbreviation_map\"})
        return conditions_list

    conds = map_abbreviations_to_conds(prompt, conds)
    is_category_search = extracted.get(\"is_category_search\", False)
    conds = deduplicate_conditions(conds)
    conds = apply_downgrade_map(conds)
    conds = inject_node_affinity(conds)
    
    # 2. Tower 1: Vector Search
    with open(\"secrets.json\", \"r\", encoding=\"utf-8\") as f:
        secrets = json.load(f)
    client = OpenAI(api_key=secrets.get(\"OPENAI_API_KEY\"))
    emb_res = client.embeddings.create(input=[prompt], model=\"text-embedding-3-small\")
    query_vector = emb_res.data[0].embedding
    
    v_scores = {}
    id_to_name = {}
    
    import os
    n_uri = os.environ.get('NEO4J_URI', 'bolt://127.0.0.1:7687')
    n_user = os.environ.get('NEO4J_USERNAME', 'neo4j')
    n_pw = os.environ.get('NEO4J_PASSWORD', 'toss1234')
    driver = GraphDatabase.driver(n_uri, auth=(n_user, n_pw))
    
    try:
        with driver.session() as session:
            res_v = session.run(\"\"\"
                CALL db.index.vector.queryNodes('candidate_embedding', 100, $queryVector)
                YIELD node AS c, score
                RETURN c.id AS id, coalesce(c.name_kr, c.name) AS name, score
            \"\"\", queryVector=query_vector)
            for r in res_v:
                cid = str(r[\"id\"])
                v_scores[cid] = r[\"score\"]
                id_to_name[cid] = r[\"name\"]
    except Exception as e:
        logger.error(f\"[V9] Vector Error: {e}\")

    # 3. Tower 2: Graph Score
    g_scores = {}
    target_skills = list(set([c.get(\"skill\") for c in conds if c.get(\"skill\")]))
    if target_skills:
        try:
            with driver.session() as session:
                res_g = session.run(\"\"\"
                    MATCH (c:Candidate)-[r]->(s:Skill)
                    WHERE s.name IN $target_skills AND type(r) <> 'USED_AS_TEMP' AND c.is_duplicate = 0
                    WITH c, collect(DISTINCT {skill: s.name, action: type(r)}) AS skills
                    RETURN coalesce(c.id, c.name_kr) AS id, coalesce(c.name_kr, c.name) AS name, skills
                \"\"\", target_skills=target_skills)
                for r in res_g:
                    cid = str(r[\"id\"])
                    cand_edges = r[\"skills\"]
                    id_to_name[cid] = r[\"name\"]
                    
                    raw_g = calculate_gravity_fusion_score(cand_edges, conds, is_category_search)
                    g_score = math.log(max(raw_g, 0) + 1) / 3.0
                    g_scores[cid] = g_score
        except Exception as e:
            logger.error(f\"[V9] Graph Error: {e}\")

    # 4. Tower 3: BM25 Score
    bm_scores = get_bm25_top(prompt, top_k=200)

    # 5. Hybrid Fusion
    all_ids = set(v_scores.keys()) | set(g_scores.keys()) | set(bm_scores.keys())
    final_candidates = []
    
    for cid in all_ids:
        v = v_scores.get(cid, 0.0)
        g = g_scores.get(cid, 0.0)
        b = bm_scores.get(cid, 0.0)
        
        final_score = (v * 0.4) + (g * 0.3) + (b * 0.3)
        
        name = id_to_name.get(cid, cache_map.get(cid, {}).get('name_kr', cid))
        final_candidates.append({
            'id': cid,
            'candidate_id': cid,
            'name': name,
            'score': final_score,
            'v_score': v,
            'g_score': g,
            'bm_score': b
        })
    
    final_candidates.sort(key=lambda x: x['score'], reverse=True)
    top_matched = final_candidates[:50]
    
    # Hydrate metadata for top results
    combined_ids = [c['id'] for c in top_matched]
    edges_map = {}
    try:
        with driver.session() as session:
            res_e = session.run(\"\"\"
                MATCH (c:Candidate)-[r]->(s:Skill)
                WHERE (c.id IN $ids OR c.name_kr IN $ids) AND type(r) <> 'USED_AS_TEMP'
                RETURN coalesce(c.id, c.name_kr) AS id, collect(DISTINCT {skill: s.name, action: type(r)}) AS skills
            \"\"\", ids=combined_ids)
            edges_map = {str(r[\"id\"]): r[\"skills\"] for r in res_e}
    except Exception as e:
        logger.error(f\"[V9] Edge hydration error: {e}\")
    finally:
        driver.close()

    matched_candidates = []
    for c in top_matched:
        cid = c['id']
        name = c['name']
        c_info = cache_map.get(cid) or cache_map.get(name) or {}
        
        cand_edges = edges_map.get(cid, [])
        matched_str_list = [f\"{e['action']}:{e['skill']}\" for e in cand_edges]
        
        candidate_obj = {
            'id': cid,
            'name_kr': name,
            'final_score': round(c['score'], 4),
            'v_score': round(c['v_score'], 4),
            'g_score': round(c['g_score'], 4),
            'bm_score': round(c['bm_score'], 4),
            'matched_skills': matched_str_list,
            'sector': c_info.get('sector', ''),
            'current_company': c_info.get('current_company', ''),
            'total_years': c_info.get('total_years', 0),
            'profile_summary': c_info.get('profile_summary', '')
        }
        matched_candidates.append(candidate_obj)

    logger.info(f\"[V9 Hybrid Search] Completed. Top result: {matched_candidates[0]['name_kr'] if matched_candidates else 'None'}\")
    
    return {
        'matched': matched_candidates,
        'total': len(final_candidates),
        'is_category_search': is_category_search
    }
"""

with open('jd_compiler.py', 'a', encoding='utf-8') as f:
    f.write(code_to_append)
print("api_search_v9 appended successfully.")
