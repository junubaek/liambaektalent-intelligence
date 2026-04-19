import math
import logging
import time
from typing import List, Dict
import json
from openai import OpenAI
from neo4j import GraphDatabase

# This script will patch jd_compiler.py directly

def patch_file():
    with open('jd_compiler.py', 'r', encoding='utf-8') as f:
        content = f.read()

    # Rewrite calculate_gravity_fusion_score
    old_func = content[content.find('def calculate_gravity_fusion_score'):content.find('logging.basicConfig')]
    
    new_func = """def calculate_gravity_fusion_score(candidate_edges, conds, is_category_search=False):
    if not conds or not isinstance(candidate_edges, list):
        return 0.0

    jd_target_skills = [c.get('skill', '') for c in conds if c.get('skill')]
    DEPTH_MULTIPLIER = {1: 1.0, 2: 1.3, 3: 1.5, 4: 1.6}

    matched_skill_actions = {}
    for edge in candidate_edges:
        if isinstance(edge, dict):
            skill = edge.get('skill', '')
            action = edge.get('action', 'MANAGED')
        else:
            skill = edge
            action = "MANAGED"
            
        if skill in jd_target_skills:
            weight = ACTION_WEIGHTS.get(action, 1.0)
            if skill not in matched_skill_actions:
                matched_skill_actions[skill] = []
            matched_skill_actions[skill].append(weight)

    matched_score = 0
    for skill, weights in matched_skill_actions.items():
        max_weight = max(weights)
        depth = min(len(weights), 4)
        depth_mult = DEPTH_MULTIPLIER[depth]
        matched_score += max_weight * depth_mult

    return matched_score

"""
    content = content.replace(old_func, new_func)
    
    # Rewrite api_search_v8
    old_api = content[content.find('def api_search_v8'):content.find('def normalize_query_with_map')]
    
    new_api = """def api_search_v8(prompt: str, session_id: str = None) -> dict:
    st = time.time()
    logger.info(f"\\n\\n[V8 API Search] Payload: {prompt} / Session: {session_id}")
    
    extracted = parse_jd_to_json(prompt)
    conds = extracted.get("conditions", [])
    is_category_search = extracted.get("is_category_search", False)
    conds = deduplicate_conditions(conds)
    conds = apply_downgrade_map(conds)
    conds = inject_node_affinity(conds)
    
    import json
    with open("secrets.json", "r", encoding="utf-8") as f:
        secrets = json.load(f)
    api_key = secrets.get("OPENAI_API_KEY") or secrets.get("openai_api_key")
    
    from openai import OpenAI
    client = OpenAI(api_key=api_key)
    from neo4j import GraphDatabase
    import math
    
    # [Phase 1: Vector Search]
    emb_res = client.embeddings.create(input=[prompt], model="text-embedding-3-small")
    query_vector = emb_res.data[0].embedding
    
    top_150_vectors = {}
    top_names = []
    
    try:
        driver = GraphDatabase.driver("bolt://127.0.0.1:7687", auth=("neo4j", "toss1234"))
        with driver.session() as session:
            q_vec = \"\"\"
            CALL db.index.vector.queryNodes('candidate_embedding', 150, $queryVector)
            YIELD node AS c, score
            RETURN c.name_kr AS name, score
            \"\"\"
            res = session.run(q_vec, queryVector=query_vector)
            for r in res:
                name = r["name"]
                if name:
                    top_150_vectors[name] = r["score"]
                    top_names.append(name)
    except Exception as e:
        logger.error(f"[V8 API Search] Neo4j Vector error: {e}")
        return {'matched': []}
        
    if not top_names:
        return {'matched': []}
        
    logger.info(f"[Phase 1] Extracted Top-150 via Neo4j Native Vector Index.")

    # [Phase 2: Graph Score]
    edges_map = {}
    try:
        with driver.session() as session:
            q = \"\"\"
            MATCH (c:Candidate)-[r]->(s:Skill)
            WHERE c.name_kr IN $names AND type(r) <> 'USED_AS_TEMP' 
            RETURN c.name_kr AS name, collect(DISTINCT {skill: s.name, action: type(r)}) AS skills
            \"\"\"
            res = session.run(q, names=top_names)
            edges_map = {r["name"]: r["skills"] for r in res}
    except Exception as e:
        logger.error(f"[V8 API Search] Neo4j Graph error: {e}")
    finally:
        driver.close()

    final_results = []
    
    for name in top_names:
        v_score = top_150_vectors.get(name, 0.0)
        cand_edges = edges_map.get(name, [])
        
        # Calculate raw graph score
        raw_graph_score = calculate_gravity_fusion_score(cand_edges, conds, is_category_search)
        
        # Log smoothing
        graph_score = math.log(max(raw_graph_score, 0) + 1)
        
        # [Phase 3: Fusion]
        if is_category_search:
            final_score = (graph_score * 0.70) + (v_score * 0.30)
        else:
            final_score = (graph_score * 0.85) + (v_score * 0.15)
            
        final_results.append({'candidate_id': name, 'name_kr': name, 'name': name, 'score': round(final_score, 4), 'total_edges': len(cand_edges)})
        
    final_results.sort(key=lambda x: (x['score'], x['total_edges']), reverse=True)
    logger.info(f"[V8 API Search] Elapsed: {time.time() - st:.3f}s / Total Hits: {len(final_results)}")
    
    return {'matched': final_results}

"""
    content = content.replace(old_api, new_api)
    with open('jd_compiler.py', 'w', encoding='utf-8') as f:
        f.write(content)

if __name__ == "__main__":
    patch_file()
    print("Patch applied.")
