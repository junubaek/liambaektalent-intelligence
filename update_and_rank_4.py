import sqlite3
import json
import sys
from neo4j import GraphDatabase

with open(r"C:\Users\cazam\Downloads\이력서자동분석검색시스템\secrets.json", "r", encoding="utf-8") as f:
    secrets = json.load(f)

n_uri = secrets.get("NEO4J_URI", "neo4j://127.0.0.1:7687")
n_user = secrets.get("NEO4J_USERNAME", "neo4j")
n_pw = secrets.get("NEO4J_PASSWORD", "toss1234")

driver = GraphDatabase.driver(n_uri, auth=(n_user, n_pw))

print("=== 1. Neo4j Edges Manual Augment ===")
with driver.session() as session:
    # 1. 김태경
    cid = 'fbc27466-7587-45e6-b459-c2920b5d71fe'
    skills = [
        ('GPU_Direct', 'BUILT', 1.8),
        ('Kubernetes', 'MANAGED', 1.8),
        ('GPU_Acceleration', 'MANAGED', 1.8),
        ('High_Performance_Computing', 'MANAGED', 1.8),
        ('Infrastructure_and_Cloud', 'MANAGED', 1.8),
    ]
    for skill, rel, w in skills:
        session.run(f'''
            MATCH (c:Candidate {{id:$cid}})
            MERGE (s:Skill {{name:$skill}})
            MERGE (c)-[r:{rel}]->(s)
            SET r.weight=$w
        ''', cid=cid, skill=skill, w=w)
    print('[김태경] 완료')

    # 2. 오수영
    cid = '32e22567-1b6f-8181-9992-d986271e941f'
    skills = [
        ('CISO_CPO_Leadership', 'MANAGED', 1.8),
        ('Information_Security', 'MANAGED', 1.8),
        ('Legal_Compliance', 'MANAGED', 1.8),
        ('CISO_CPO_Leadership', 'BUILT', 1.7),
        ('Information_Security', 'BUILT', 1.7),
    ]
    for skill, rel, w in skills:
        session.run(f'''
            MATCH (c:Candidate {{id:$cid}})
            MERGE (s:Skill {{name:$skill}})
            MERGE (c)-[r:{rel}]->(s)
            SET r.weight=$w
        ''', cid=cid, skill=skill, w=w)
    print('[오수영] 완료')

    # 3. 김형수
    cid = '4b4c3372-401b-4897-a9b3-d36a3ba3de37'
    skills = [
        ('Venture_Capital', 'MANAGED', 1.8),
        ('Venture_Capital_Fundraising', 'MANAGED', 1.8),
        ('Corporate_Funding', 'MANAGED', 1.8),
        ('Venture_Capital', 'BUILT', 1.7),
        ('Venture_Capital_Fundraising', 'BUILT', 1.7),
        ('Business_Development', 'MANAGED', 1.8),
    ]
    for skill, rel, w in skills:
        session.run(f'''
            MATCH (c:Candidate {{id:$cid}})
            MERGE (s:Skill {{name:$skill}})
            MERGE (c)-[r:{rel}]->(s)
            SET r.weight=$w
        ''', cid=cid, skill=skill, w=w)
    print('[김형수] 완료')

    # 4. 박천혁
    cid = '3d322d13-0699-4453-b70e-5a4c2aac38f9'
    session.run('''
        MATCH (c:Candidate {id:$cid})-[r]->(s:Skill {name:"Chiplet_Architecture"})
        DELETE r
    ''', cid=cid)
    skills = [
        ('CUDA', 'MANAGED', 1.8),
        ('High_Performance_Computing', 'MANAGED', 1.8),
        ('GPU_Acceleration', 'MANAGED', 1.8),
        ('Rust', 'MANAGED', 1.8),
        ('CUDA', 'BUILT', 1.7),
        ('High_Performance_Computing', 'BUILT', 1.7),
    ]
    for skill, rel, w in skills:
        session.run(f'''
            MATCH (c:Candidate {{id:$cid}})
            MERGE (s:Skill {{name:$skill}})
            MERGE (c)-[r:{rel}]->(s)
            SET r.weight=$w
        ''', cid=cid, skill=skill, w=w)
    print('[박천혁] 완료')

driver.close()

# 2. Rank check using api_search_v9
print("\n=== 2. Rank checks ===")
sys.path.append(r'C:\Users\cazam\Downloads\이력서자동분석검색시스템')
from jd_compiler import api_search_v9

tests = [
    ('GPU virtualization AI datacenter HPC network infra', 'MIDDLE', 'fbc27466-7587-45e6-b459-c2920b5d71fe', '김태경'),
    ('CISO information security game company', 'SENIOR', '32e22567-1b6f-8181-9992-d986271e941f', '오수영'),
    ('VC venture capital deal sourcing portfolio startup', 'SENIOR', '4b4c3372-401b-4897-a9b3-d36a3ba3de37', '김형수'),
    ('HPC CUDA parallel computing C++ Rust GPU', 'MIDDLE', '3d322d13-0699-4453-b70e-5a4c2aac38f9', '박천혁'),
]

for query, seniority, target_id, name in tests:
    r = api_search_v9(query, seniority=seniority)
    matched = r.get('matched', [])
    rank = next((i+1 for i,c in enumerate(matched) if c.get('id')==target_id), None)
    top3 = [(c.get('name_kr','?')[:6], c.get('id','')[:8]) for c in matched[:3]]
    print(f'[{name}] rank={rank} | top3={top3}')
