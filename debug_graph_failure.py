import json
import sys
import os
from neo4j import GraphDatabase

# Ensure UTF-8 output
sys.stdout.reconfigure(encoding='utf-8')

def _get_secret(key):
    with open('secrets.json', 'r', encoding='utf-8') as f:
        s = json.load(f)
    return s.get(key)

n_uri = _get_secret('NEO4J_URI')
n_user = _get_secret('NEO4J_USERNAME')
n_pw = _get_secret('NEO4J_PASSWORD')

driver = GraphDatabase.driver(n_uri, auth=(n_user, n_pw))

def run_debug():
    sample_query = "경영전략을 수립하고 자금 운용(Treasury) 및 외환 관리를 총괄하며, ERP 시스템을 구축해본 재무 전문가"
    
    from jd_compiler import parse_jd_to_json
    extracted = parse_jd_to_json(sample_query)
    conds = extracted.get("conditions", [])
    target_skills = list(set([c.get("skill") for c in conds if c.get("skill")]))
    
    print(f"--- [Step 1] Extracted Target Skills ---")
    print(f"Skills: {target_skills}")
    
    with driver.session() as session:
        # 2. Neo4j 노드 매칭 확인
        print(f"\n--- [Step 2] Neo4j Skill Node Match Check ---")
        q_node = "MATCH (s:Skill) WHERE s.name IN $skills RETURN s.name AS name, count(*) AS count"
        res_node = session.run(q_node, skills=target_skills)
        matched_nodes = []
        for r in res_node:
            matched_nodes.append(r['name'])
            print(f"Found Node in DB: {r['name']}")
        
        if not matched_nodes:
            print("❌ No matching Skill nodes found in Neo4j.")
            print("\nSample Skills from DB for comparison:")
            q_sample = "MATCH (s:Skill) RETURN s.name LIMIT 10"
            for r in session.run(q_sample):
                print(f" - '{r['s.name']}'")
        
        # 3. Candidate 연결 확인
        if matched_nodes:
            print(f"\n--- [Step 3] Candidate Connectivity Check ---")
            q_conn = "MATCH (c:Candidate)-[r]->(s:Skill) WHERE s.name IN $matched RETURN s.name, count(c) AS candidates"
            res_conn = session.run(q_conn, matched=matched_nodes)
            for r in res_conn:
                print(f"Skill: {r['s.name']} | Candidates: {r['candidates']}")
        
        # 4. Baseline Test (Python)
        print(f"\n--- [Step 4] Baseline Test (Python) ---")
        q_base = "MATCH (c:Candidate)-[r]->(s:Skill) WHERE s.name = 'Python' RETURN count(c) AS count"
        res_base = session.run(q_base)
        for r in res_base:
            print(f"Python Candidates in DB: {r['count']}")

if __name__ == "__main__":
    try:
        run_debug()
    finally:
        driver.close()
