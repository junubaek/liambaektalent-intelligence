import json
from neo4j import GraphDatabase

with open(r"C:\Users\cazam\Downloads\이력서자동분석검색시스템\secrets.json", "r", encoding="utf-8") as f:
    secrets = json.load(f)

n_uri = secrets.get("NEO4J_URI", "neo4j://127.0.0.1:7687")
n_user = secrets.get("NEO4J_USERNAME", "neo4j")
n_pw = secrets.get("NEO4J_PASSWORD", "toss1234")

driver = GraphDatabase.driver(n_uri, auth=(n_user, n_pw))

targets = [
    ('fbc27466-7587-45e6-b459-c2920b5d71fe', '김태경'),
    ('32e22567-1b6f-8181-9992-d986271e941f', '오수영'),
    ('4b4c3372-401b-4897-a9b3-d36a3ba3de37', '김형수'),
    ('3d322d13-0699-4453-b70e-5a4c2aac38f9', '박천혁'),
]

with driver.session() as session:
    for cid, name in targets:
        # We fetch weight or confidence (whichever is available) to avoid None issues.
        res = list(session.run(
            'MATCH (c:Candidate {id:$cid})-[r]->(s:Skill) '
            'RETURN s.name as name, type(r) as rel, coalesce(r.weight, r.confidence) as w '
            'ORDER BY w DESC',
            cid=cid
        ))
        print(f'[{name}] {len(res)}개 엣지')
        for r in res:
            weight_val = r["w"]
            # Formatting weight_val to show clean decimal if float
            w_str = f"{weight_val:.2f}" if isinstance(weight_val, float) else str(weight_val)
            print(f'  {r["name"]} | {r["rel"]} | w={w_str}')
        print()

driver.close()
