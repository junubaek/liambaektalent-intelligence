import sys, os, math, sqlite3, json, re
sys.stdout.reconfigure(encoding='utf-8')
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT_DIR)
os.chdir(ROOT_DIR)

from jd_compiler import (
    parse_jd_to_json, calculate_gravity_fusion_score, calc_gravity_score, 
    calc_achievement_density, get_bm25_top, get_candidates_from_cache,
    apply_downgrade_map, inject_node_affinity, deduplicate_conditions,
    get_company_boost
)
from neo4j import GraphDatabase
from openai import OpenAI

def debug_full_search(prompt, target_id):
    secrets = json.load(open('secrets.json'))
    oai = OpenAI(api_key=secrets['OPENAI_API_KEY'])
    driver = GraphDatabase.driver(secrets['NEO4J_URI'], auth=(secrets['NEO4J_USERNAME'], secrets['NEO4J_PASSWORD']))
    
    # 1. Parse
    extracted = parse_jd_to_json(prompt)
    conds = extracted.get("conditions", [])
    print(f"Extracted Conditions: {conds}")
    target_skills = [c.get("skill") for c in conds if c.get("skill")]
    
    # 2. Vector Search
    emb_res = oai.embeddings.create(input=[prompt], model="text-embedding-3-small")
    query_vector = emb_res.data[0].embedding
    
    v_scores = {}
    with driver.session() as session:
        res_v = session.run("""
            CALL db.index.vector.queryNodes('candidate_embedding', 200, $queryVector)
            YIELD node AS c, score
            RETURN c.id AS id, score
        """, queryVector=query_vector)
        for r in res_v:
            v_scores[str(r["id"])] = r["score"]
    
    print(f"Target in Vector Tower: {target_id in v_scores} (Rank: {list(v_scores.keys()).index(target_id)+1 if target_id in v_scores else 'N/A'}, Score: {v_scores.get(target_id)})")
    
    # 3. Graph Match
    g_matched_ids = []
    with driver.session() as session:
        res_g = session.run("""
            MATCH (c:Candidate)-[r]->(s:Skill)
            WHERE s.name IN $target_skills AND type(r) <> 'USED_AS_TEMP' 
            RETURN DISTINCT coalesce(c.id, c.name_kr) AS id
        """, target_skills=target_skills)
        g_matched_ids = [str(r["id"]) for r in res_g]
    
    print(f"Target in Graph Tower Match: {target_id in g_matched_ids} (Rank: {g_matched_ids.index(target_id)+1 if target_id in g_matched_ids else 'N/A'} of {len(g_matched_ids)})")
    
    # 4. Pool
    vector_ids = list(v_scores.keys())
    graph_ids = g_matched_ids[:300]
    bm_scores = get_bm25_top(prompt, top_k=200)
    bm25_ids = sorted(bm_scores.keys(), key=lambda k: bm_scores[k], reverse=True)[:100]
    
    combined_ids = list(set(vector_ids) | set(graph_ids) | set(bm25_ids))
    print(f"Target in Combined Pool: {target_id in combined_ids}")
    
    if target_id not in combined_ids:
        print("❌ Target excluded from pool. Search ending.")
        driver.close()
        return

    # 5. Score Components for Target
    with driver.session() as session:
        res_e = session.run("""
            MATCH (c:Candidate)-[r]->(s:Skill)
            WHERE (c.id = $id OR c.name_kr = $id) AND type(r) <> 'USED_AS_TEMP'
            RETURN collect({skill: s.name, action: type(r)}) AS skills
        """, id=target_id).single()
        cand_edges = res_e["skills"] if res_e else []
    
    conn = sqlite3.connect('candidates.db')
    cur = conn.cursor()
    cur.execute("SELECT raw_text, total_years, program_signal FROM candidates WHERE id = ?", (target_id,))
    row = cur.fetchone()
    raw_text = row[0] if row else ""
    total_years = row[1] if row else 0
    prog_signal = row[2] if row else 0.0
    
    seniority = "SENIOR" if total_years >= 10 else ("MIDDLE" if total_years >= 5 else "JUNIOR")
    
    raw_g = calculate_gravity_fusion_score(cand_edges, conds)
    raw_g += calc_gravity_score([e['skill'] for e in cand_edges], [c['skill'] for c in conds], seniority)
    g_score = math.log(max(raw_g, 0) + 1)
    
    matched_action_score = sum(0.3 for edge in cand_edges if edge['skill'] in target_skills) / max(len(target_skills), 1)
    depth_action = min(matched_action_score, 1.0)
    achievement_density = calc_achievement_density(raw_text)
    d_score = (depth_action * 0.6) + (achievement_density * 0.4)
    
    b_score = bm_scores.get(target_id, 0.0)
    v_score = v_scores.get(target_id, 0.0)
    
    print(f"\n--- Final Scores for {target_id} ---")
    print(f"Raw V: {v_score:.4f}")
    print(f"Raw G: {g_score:.4f} (Fusion+Gravity: {raw_g})")
    print(f"Raw B: {b_score:.4f}")
    print(f"Raw D: {d_score:.4f}")
    
    driver.close()
    conn.close()

debug_full_search("Overseas Sales Manager", "898ea4e0-77d4-46d5-bf4d-c2d5b4a04741")
