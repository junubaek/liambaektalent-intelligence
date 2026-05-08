import sqlite3
import json
import re
import os
import sys
from collections import defaultdict
from neo4j import GraphDatabase

# Ensure UTF-8 output
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

# Root directory check
ROOT_DIR = os.path.dirname(os.path.abspath(os.path.dirname(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from ontology_graph import CANONICAL_MAP

# 동사 패턴 및 우선순위
ACTION_PATTERNS = {
    'BUILT': re.compile(r'구축|개발|만들었|개발했|설계했|built|developed|created|implemented'),
    'DESIGNED': re.compile(r'설계|기획|아키텍처|designed|architected|planned'),
    'LED': re.compile(r'총괄|리드|이끌었|주도|led|managed team|팀장|본부장|임원'),
    'LAUNCHED': re.compile(r'런칭|출시|런치|launched|released|deployed'),
    'ANALYZED': re.compile(r'분석|검토|연구|analyzed|researched|reviewed'),
    'GREW': re.compile(r'성장|확장|늘렸|grew|scaled|expanded|increased'),
    'NEGOTIATED': re.compile(r'협상|계약|체결|negotiated|contracted|partnered')
}
ACTION_PRIORITY = ['BUILT', 'DESIGNED', 'LED', 'LAUNCHED', 'ANALYZED', 'GREW', 'NEGOTIATED', 'MANAGED']

def extract_skills_with_actions(text, sorted_keys):
    if not text: return {}
    lower_text = text.lower()
    skill_to_action = {}
    
    for k in sorted_keys:
        k_lower = k.lower()
        if k_lower in lower_text:
            # Boundary check for English
            if re.search(r'[a-z]', k_lower):
                pattern = r'(?<![a-z0-9])' + re.escape(k_lower) + r'(?![a-z0-9])'
                if not re.search(pattern, lower_text):
                    continue
            
            skill_name = CANONICAL_MAP[k]
            
            # Context (Window: 60 chars)
            idx = lower_text.find(k_lower)
            start = max(0, idx - 60)
            end = min(len(lower_text), idx + len(k_lower) + 60)
            context = lower_text[start:end]
            
            best_action = 'MANAGED'
            for action in ACTION_PRIORITY[:-1]:
                if ACTION_PATTERNS[action].search(context):
                    best_action = action
                    break
            
            if skill_name not in skill_to_action:
                skill_to_action[skill_name] = best_action
            else:
                curr_idx = ACTION_PRIORITY.index(skill_to_action[skill_name])
                new_idx = ACTION_PRIORITY.index(best_action)
                if new_idx < curr_idx:
                    skill_to_action[skill_name] = best_action
                        
    return skill_to_action

def full_resync_with_actions():
    # 1. Load Secrets
    secrets_path = 'secrets.json'
    with open(secrets_path, 'r', encoding='utf-8') as f:
        secrets = json.load(f)

    # 2. Connect
    conn = sqlite3.connect('candidates.db', timeout=30)
    cur = conn.cursor()
    driver = GraphDatabase.driver(secrets['NEO4J_URI'], auth=(secrets['NEO4J_USERNAME'], secrets['NEO4J_PASSWORD']))

    # 3. Data Prep
    sorted_keys = sorted(CANONICAL_MAP.keys(), key=len, reverse=True)
    cur.execute("SELECT id, raw_text FROM candidates WHERE raw_text IS NOT NULL")
    candidates = cur.fetchall()
    total = len(candidates)
    
    print(f"--- Starting High-Speed Batch Resync for {total} Candidates ---")

    batch_size = 50 # 50명씩 배치
    
    for i in range(0, total, batch_size):
        batch = candidates[i:i+batch_size]
        batch_results = []
        
        for cid, raw_text in batch:
            skills_map = extract_skills_with_actions(raw_text, sorted_keys)
            if skills_map:
                groups = defaultdict(list)
                for s, a in skills_map.items():
                    groups[a].append(s)
                batch_results.append({'id': cid, 'groups': dict(groups)})
            else:
                batch_results.append({'id': cid, 'groups': {}})

        # Neo4j Batch Transaction
        with driver.session() as session:
            def tx_work(tx):
                for res in batch_results:
                    # 1. Delete
                    tx.run("MATCH (c:Candidate {id: $id})-[r]->(s:Skill) DELETE r", id=res['id'])
                    # 2. Insert by action type
                    for action, skills in res['groups'].items():
                        tx.run(f"""
                            MATCH (c:Candidate {{id: $id}})
                            UNWIND $skills as sk_name
                            MERGE (s:Skill {{name: sk_name}})
                            MERGE (c)-[:{action}]->(s)
                        """, id=res['id'], skills=skills)
            
            try:
                session.execute_write(tx_work)
                # SQLite Update
                batch_ids = [r['id'] for r in batch_results]
                cur.executemany("UPDATE candidates SET is_neo4j_synced = 1 WHERE id = ?", [(bid,) for bid in batch_ids])
                conn.commit()
                print(f"Progress: {min(i + batch_size, total)}/{total} ({(min(i + batch_size, total))/total*100:.1f}%)", flush=True)
            except Exception as e:
                print(f"Error in batch starting at {i}: {e}")

    conn.close()
    driver.close()
    print("--- Full Resync Complete ---")

if __name__ == "__main__":
    full_resync_with_actions()
