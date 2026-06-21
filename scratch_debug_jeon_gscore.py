import sys
import os
import json
import sqlite3

# Ensure UTF-8 output
sys.stdout.reconfigure(encoding='utf-8')
sys.path.append(r'C:\Users\cazam\Downloads\이력서자동분석검색시스템')

from neo4j import GraphDatabase
from ontology_graph import CANONICAL_MAP, UNIFIED_GRAVITY_FIELD, SENIOR_EXPANDED_SYNERGY
from jd_compiler import (
    parse_jd_to_json,
    deduplicate_conditions,
    apply_downgrade_map,
    inject_node_affinity,
    calculate_gravity_fusion_score,
    calc_gravity_score
)

secrets_path = r"C:\Users\cazam\Downloads\이력서자동분석검색시스템\secrets.json"
with open(secrets_path, "r", encoding="utf-8") as f:
    secrets = json.load(f)

n_uri = secrets.get("NEO4J_URI", "neo4j://127.0.0.1:7687")
n_user = secrets.get("NEO4J_USERNAME", "neo4j")
n_pw = secrets.get("NEO4J_PASSWORD", "toss1234")

# [1] Query parsing
prompt = 'NPU 드라이버 커널 엔지니어 찾아줘'
print(f"1. Parsing query: '{prompt}'...")
extracted = parse_jd_to_json(prompt)
conds = extracted.get("conditions", [])

# Map abbreviations
def map_abbreviations_to_conds(query_str, conditions_list):
    expansion_map = {
        "IPO": ["Investor_Relations", "IPO_Preparation"],
        "IR": ["Investor_Relations"], "DFT": ["Design_for_Testability"],
        "RTL": ["RTL_Design"], "SoC": ["System_on_Chip"], "SAP": ["SAP_ERP"],
        "BI": ["Business_Intelligence"], "Tableau": ["Tableau"],
        "DevOps": ["DevOps", "CI_CD"], "SaaS": ["SaaS"],
        "Kotlin": ["Kotlin", "Android_Development"], "ASRS": ["Warehouse_Automation"]
    }
    import re
    for abbr, expansions in expansion_map.items():
        if re.search(r'\b' + re.escape(abbr) + r'\b', query_str, re.IGNORECASE):
            for exp in expansions:
                if not any(c.get('skill') == exp for c in conditions_list):
                    conditions_list.append({"action": "MANAGED", "skill": exp, "is_mandatory": False, "source": "abbreviation_map"})
    return conditions_list

conds = map_abbreviations_to_conds(prompt, conds)
conds = deduplicate_conditions(conds)
conds = apply_downgrade_map(conds)
conds = inject_node_affinity(conds)

query_nodes = [c['skill'] for c in conds]
print(f"   -> Parsed Target Skills (Query Nodes): {query_nodes}")

# [2] Fetch Jeon Hyeongjun's edges
print("\n2. Fetching Hyeongjun Jeon's edges from Neo4j...")
driver = GraphDatabase.driver(n_uri, auth=(n_user, n_pw))
cand_edges = []
try:
    with driver.session() as session:
        res = session.run("""
            MATCH (c:Candidate)-[r]->(s:Skill)
            WHERE c.name_kr = '전형준' OR c.name = 'Hyeongjun Jeon' OR c.name = '전형준'
            RETURN s.name AS skill, type(r) AS action
        """)
        for r in res:
            cand_edges.append({'skill': r['skill'], 'action': r['action']})
finally:
    driver.close()

print(f"   -> Retrieved {len(cand_edges)} edges from Neo4j. Sample: {cand_edges[:5]}")

# [3] Trace gravity fusion score and gravity score for Jeon Hyeongjun
print("\n3. Simulating G Score Calculation for Hyeongjun Jeon...")
jd_target_skills = [c.get('skill', '') for c in conds if c.get('skill')]
print(f"   JD Target Skills: {jd_target_skills}")

# Detailed check of s.name directly in matched_skill_actions
print("\n   [Gravity Fusion Score Tracing]")
ACTION_WEIGHTS = {
    'BUILT': 2.0, 'DESIGNED': 1.9, 'CLOSED': 1.4, 'LED': 1.4, 'MIGRATED': 1.7,
    'DEPLOYED': 1.6, 'OPTIMIZED': 1.5, 'RESOLVED': 1.5, 'ANALYZED': 1.4,
    'INTEGRATED': 1.4, 'LAUNCHED': 1.4, 'GREW': 1.4, 'PLANNED': 1.3,
    'DRAFTED': 1.3, 'EXECUTED': 1.3, 'NEGOTIATED': 1.3, 'MANAGED': 1.0,
    'OPERATED': 1.0, 'SUPPORTED': 1.0, 'USED': 0.3
}
DEPTH_MULTIPLIER = {1: 1.0, 2: 1.1, 3: 1.2, 4: 1.3}

matched_skill_actions = {}
for edge in cand_edges:
    skill = edge.get('skill', '')
    action = edge.get('action', 'MANAGED')
    
    # Trace specific NPU skills
    if 'npu' in skill.lower() or 'kernel' in skill.lower():
        print(f"     Skill: '{skill}' | Action: '{action}' | Target skill match?: {skill in jd_target_skills}")
        
    if skill in jd_target_skills:
        weight = ACTION_WEIGHTS.get(action, 1.0)
        matched_skill_actions.setdefault(skill, []).append(weight)

raw_g = 0
for skill, weights in matched_skill_actions.items():
    max_weight = max(weights)
    depth = min(len(weights), 4)
    depth_mult = DEPTH_MULTIPLIER[depth]
    addition = max_weight * depth_mult
    raw_g += addition
    print(f"     -> Matched skill: '{skill}' | Weights: {weights} | Max: {max_weight} | Depth: {depth} | Added Score: {addition:.4f}")

print(f"   Total gravity fusion score: {raw_g:.4f}")

# Unified gravity score
print("\n   [Gravity Score Tracing]")
candidate_nodes = [e['skill'] for e in cand_edges]
print(f"     Candidate Nodes: {candidate_nodes}")

gravity_addition = 0
REPEL_MULTIPLIER = {"SENIOR": 0.5, "MIDDLE": 0.7, "JUNIOR": 0.9, "All": 0.7}
repel_mult = 0.7

for node in query_nodes:
    field = UNIFIED_GRAVITY_FIELD.get(node, {})
    core = field.get("core_attracts", {})
    synergy = field.get("synergy_attracts", {})
    repels = field.get("repels", {})
    
    node_score = 0
    for cnode, weight in core.items():
        if cnode in candidate_nodes:
            node_score += weight * 2.0
            print(f"     Core Attraction match! Query Node: '{node}' -> Candidate Node: '{cnode}' | Weight: {weight}*2.0")
            
    for snode, weight in synergy.items():
        if snode in candidate_nodes:
            node_score += weight
            print(f"     Synergy Attraction match! Query Node: '{node}' -> Candidate Node: '{snode}' | Weight: {weight}")
            
    for rnode, weight in repels.items():
        if rnode in candidate_nodes:
            node_score += weight * repel_mult
            print(f"     Repels match! Query Node: '{node}' -> Candidate Node: '{rnode}' | Weight: {weight}*{repel_mult}")
            
    gravity_addition += node_score

print(f"   Total Gravity Score Added: {gravity_addition:.4f}")
final_raw_g = raw_g + gravity_addition
import math
final_g_score = math.log(max(final_raw_g, 0) + 1)
print(f"   Final G Score (log(raw + 1)): {final_g_score:.4f}")
