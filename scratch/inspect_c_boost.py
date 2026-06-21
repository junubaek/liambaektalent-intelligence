import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import json, sqlite3, math
from openai import OpenAI
from neo4j import GraphDatabase
from jd_compiler import api_search_v9

secrets = json.load(open('secrets.json', encoding='utf-8'))
client = OpenAI(api_key=secrets['OPENAI_API_KEY'])

# Run the search API but let's intercept or calculate scores manually or inspect the pool
# We can just simulate the scoring for 배성호 and print all intermediates
from jd_compiler import parse_jd_with_llm, parse_jd_to_json, calculate_gravity_fusion_score, calc_gravity_score, calc_achievement_density, get_company_boost, get_cei_boost, cosine_similarity, get_best_similarity

prompt = "카카오 출신 백엔드 시니어 개발자"
target_id = 'ba99c86f-562d-4193-8380-0e414bd19093' # 배성호

conn = sqlite3.connect('candidates.db')
cur = conn.cursor()
cur.execute("""
    SELECT id, name_kr, raw_text, sector, current_company, total_years, 
           profile_summary, careers_json, education_json, email, phone, birth_year, google_drive_url,
           program_signal, program_stage
    FROM candidates 
    WHERE id = ?
""", (target_id,))
r = cur.fetchone()

# Parse query
extracted = parse_jd_to_json(prompt)
conds = extracted.get("conditions", [])
_jd_llm = parse_jd_with_llm(prompt, client)
preferred_companies = _jd_llm.get("preferred_companies", [])

# Let's get his edges
driver = GraphDatabase.driver(secrets['NEO4J_URI'], auth=(secrets['NEO4J_USERNAME'], secrets['NEO4J_PASSWORD']))
with driver.session() as session:
    res_e = session.run("""
        MATCH (c:Candidate)-[r]->(s:Skill)
        WHERE c.id = $id AND type(r) <> 'USED_AS_TEMP'
        RETURN collect(DISTINCT {skill: s.name, action: type(r), last_used_year: r.last_used_year}) AS skills
    """, id=target_id)
    cand_edges = []
    from jd_compiler import CANONICAL_MAP
    def normalize_skill(skill_name: str) -> str:
        if skill_name in CANONICAL_MAP:
            return CANONICAL_MAP[skill_name]
        lower = skill_name.lower()
        for key, val in CANONICAL_MAP.items():
            if key.lower() == lower:
                return val
        return skill_name
        
    for row in res_e:
        for s in row["skills"]:
            cand_edges.append({
                "skill": normalize_skill(s["skill"]),
                "action": s["action"],
                "last_used_year": s.get("last_used_year")
            })
            
    # Fetch embeddings
    res_emb = session.run("""
        MATCH (c:Candidate {id: $id})
        RETURN c.embedding AS embedding, c.career_embeddings_json AS career_embeddings_json
    """, id=target_id)
    emb_row = res_emb.single()
    embedding = emb_row['embedding']
    career_json = emb_row['career_embeddings_json']

driver.close()

# Calculate similarity
emb_res = client.embeddings.create(input=[prompt], model="text-embedding-3-small")
query_vector = emb_res.data[0].embedding

main_sim = cosine_similarity(query_vector, embedding)
blended_sim = get_best_similarity(query_vector, main_sim, career_json)

# Scores
# w_v = 0.60, w_g = 0.28, w_b = 0.05, w_d = 0.07
# But wait, max_v/max_g/max_b normalization values are needed. Let's assume them from typical runs:
# max_v = 0.65, max_g = 3.0, max_b = 20.0 (BM25 max is often around 15-25)
raw_g = calculate_gravity_fusion_score(cand_edges, conds, False)
raw_g += calc_gravity_score([e['skill'] for e in cand_edges], [c['skill'] for c in conds], 'Senior')
# Apply sector discount
g_score = math.log(max(raw_g, 0) + 1)

# Depth score
matched_action_score = sum(
    1.0 if edge['action'] == 'MANAGED' else 0.7
    for edge in cand_edges
    if edge['skill'] in [c.get('skill') for c in conds if c.get('skill')]
)
achievement_density = calc_achievement_density(r[2])
depth_score = (matched_action_score * 0.6) + (achievement_density * 0.4)

c_boost = get_company_boost(r[4], conds, conn)
cei_boost = get_cei_boost(target_id, conn, 'sw')

print(f"배성호 Raw Scores:")
print(f"  Main Sim: {main_sim:.4f}")
print(f"  Blended Sim: {blended_sim:.4f}")
print(f"  G Score (raw): {raw_g:.4f} -> log: {g_score:.4f}")
print(f"  Depth Score: {depth_score:.4f}")
print(f"  Company Boost (c_boost): {c_boost:.4f}")
print(f"  CEI Boost (cei_boost): {cei_boost:.4f}")

conn.close()
