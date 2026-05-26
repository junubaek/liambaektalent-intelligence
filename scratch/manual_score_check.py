import sys, os, math
sys.stdout.reconfigure(encoding='utf-8')
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT_DIR)
os.chdir(ROOT_DIR)

from jd_compiler import parse_jd_to_json, calculate_gravity_fusion_score, calc_gravity_score, calc_achievement_density
from neo4j import GraphDatabase
import json

target_id = 'db752f0f-0f1a-437c-a09d-43c20442ab7b'
prompt = "General Affairs Manager"

# 1. Parse query
extracted = parse_jd_to_json(prompt)
conds = extracted['conditions']
print(f"Conditions: {conds}")

# 2. Get candidate data from Neo4j
secrets = json.load(open('secrets.json'))
driver = GraphDatabase.driver(secrets['NEO4J_URI'], auth=(secrets['NEO4J_USERNAME'], secrets['NEO4J_PASSWORD']))

with driver.session() as session:
    res = session.run("""
        MATCH (c:Candidate {id: $id})-[r]->(s:Skill)
        RETURN s.name as skill, type(r) as action
    """, id=target_id)
    edges = [{'skill': r['skill'], 'action': r['action']} for r in res]
    
    res_meta = session.run("MATCH (c:Candidate {id: $id}) RETURN c.profile_summary as summary, c.seniority as seniority", id=target_id).single()
    seniority = res_meta['seniority'] if res_meta else 'All'

print(f"Edges: {edges}")

# 3. Calculate Scores
g_fusion = calculate_gravity_fusion_score(edges, conds)
g_gravity = calc_gravity_score([e['skill'] for e in edges], [c['skill'] for c in conds], seniority)
g_total = g_fusion + g_gravity
g_norm = math.log(max(g_total, 0) + 1)

print(f"Fusion: {g_fusion}, Gravity: {g_gravity}, Total: {g_total}, Log-Norm: {g_norm}")

driver.close()
