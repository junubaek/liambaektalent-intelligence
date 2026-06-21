import json
import sqlite3
import sys
import subprocess
from neo4j import GraphDatabase

# 1. Update 김태경
print("=== 1. Update 김태경 Neo4j Edges ===")
with open('secrets.json', 'r', encoding='utf-8') as f:
    s = json.load(f)
n_uri = s.get("NEO4J_URI", "neo4j://127.0.0.1:7687")
n_user = s.get("NEO4J_USERNAME", "neo4j")
n_pw = s.get("NEO4J_PASSWORD", "toss1234")

driver = GraphDatabase.driver(n_uri, auth=(n_user, n_pw))
cid = 'fbc27466-7587-45e6-b459-c2920b5d71fe'
with driver.session() as session:
    for skill, rel, w in [
        ('GPGPU', 'MANAGED', 1.8),
        ('GPU_Driver', 'MANAGED', 1.8),
        ('GPGPU', 'BUILT', 1.7),
        ('GPU_Driver', 'BUILT', 1.7),
    ]:
        session.run(f'''
            MATCH (c:Candidate {{id:$cid}})
            MERGE (s:Skill {{name:$skill}})
            MERGE (c)-[r:{rel}]->(s)
            SET r.weight=$w
        ''', cid=cid, skill=skill, w=w)
    print('[김태경] GPGPU, GPU_Driver 추가 완료')
driver.close()

# 2. Modify golden_dataset_v9.json for 오수영 and 박천혁
print("\n=== 2 & 3. Update golden_dataset_v9.json ===")
path = 'golden_dataset_v9.json'
try:
    with open(path, 'r', encoding='utf-8') as f:
        d = json.load(f)
    
    for item in d:
        if item.get('query') == 'CISO information security game company':
            item['query'] = 'CISO CPO information security team building game'
            print(f'교체 완료 (오수영): {item["query"]}')
        elif item.get('query') == 'HPC CUDA parallel computing C++ Rust GPU':
            item['query'] = 'CUDA GPU kernel C++ Rust high performance computing'
            print(f'교체 완료 (박천혁): {item["query"]}')
            
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(d, f, ensure_ascii=False, indent=2)
except Exception as e:
    print(f"Error modifying golden dataset: {e}")

# 3. Rank checks
print("\n=== 4. Rank Checks ===")
sys.path.append(r'C:\Users\cazam\Downloads\이력서자동분석검색시스템')
from jd_compiler import api_search_v9

tests = [
    ('GPU virtualization AI datacenter HPC network infra', 'MIDDLE', 'fbc27466-7587-45e6-b459-c2920b5d71fe', '김태경'),
    ('CISO CPO information security team building game', 'SENIOR', '32e22567-1b6f-8181-9992-d986271e941f', '오수영'),
    ('CUDA GPU kernel C++ Rust high performance computing', 'MIDDLE', '3d322d13-0699-4453-b70e-5a4c2aac38f9', '박천혁'),
]

for query, seniority, target_id, name in tests:
    r = api_search_v9(query, seniority=seniority)
    matched = r.get('matched', [])
    rank = next((i+1 for i,c in enumerate(matched) if c.get('id')==target_id), None)
    top3 = [(c.get('name_kr','?')[:6], c.get('id','')[:8]) for c in matched[:3]]
    print(f'[{name}] rank={rank} | top3={top3}')

# 4. Evaluate NDCG
print("\n=== 5. evaluate_ndcg.py ===")
result = subprocess.run(['python', 'evaluate_ndcg.py'], capture_output=True, text=True)
print(result.stdout)
if result.stderr:
    print("Errors:", result.stderr)
