import sys, os, json
sys.stdout.reconfigure(encoding='utf-8')
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT_DIR)
os.chdir(ROOT_DIR)

from jd_compiler import parse_jd_to_json, calculate_gravity_fusion_score
from neo4j import GraphDatabase

target_id = '32022567-1b6f-8140-9d49-f3f038b20c5f'
prompt = "General Affairs Manager"

secrets = json.load(open('secrets.json'))
driver = GraphDatabase.driver(secrets['NEO4J_URI'], auth=(secrets['NEO4J_USERNAME'], secrets['NEO4J_PASSWORD']))

# 1. Parse
extracted = parse_jd_to_json(prompt)
conds = extracted.get("conditions", [])
target_skills = [c.get("skill") for c in conds if c.get("skill")]
print(f"Target Skills: {target_skills}")

# 2. Get edges
with driver.session() as session:
    res = session.run("MATCH (c:Candidate {id: $id})-[r]->(s:Skill) RETURN s.name as skill, type(r) as action", id=target_id)
    edges = [dict(r) for r in res]

# 3. Check fusion match
matched = []
for edge in edges:
    if edge['skill'] in target_skills:
        matched.append(edge)

print(f"Matched Edges for Fusion: {matched}")

# 4. Calculate score
score = calculate_gravity_fusion_score(edges, conds)
print(f"Fusion Score: {score}")

driver.close()
