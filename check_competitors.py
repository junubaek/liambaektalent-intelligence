import json
from neo4j import GraphDatabase

with open(r"C:\Users\cazam\Downloads\이력서자동분석검색시스템\secrets.json", "r", encoding="utf-8") as f:
    secrets = json.load(f)

n_uri = secrets.get("NEO4J_URI", "neo4j://127.0.0.1:7687")
n_user = secrets.get("NEO4J_USERNAME", "neo4j")
n_pw = secrets.get("NEO4J_PASSWORD", "toss1234")

driver = GraphDatabase.driver(n_uri, auth=(n_user, n_pw))

with driver.session() as session:
    for cid_prefix, label in [
        ('33522567-1b6f-81c1', '김태경1위'),
        ('341e6ee6', '오수영1위'),
        ('31f22567-1b6f-81', '박천혁1위'),
    ]:
        res = list(session.run(
            "MATCH (c:Candidate)-[r]->(s:Skill) "
            "WHERE c.id STARTS WITH $prefix "
            "RETURN c.id as cid, coalesce(c.name_kr, c.name) as name_kr, s.name as name, type(r) as rel, coalesce(r.weight, r.confidence) as w "
            "ORDER BY w DESC LIMIT 10",
            prefix=cid_prefix
        ))
        if res:
            name_val = res[0]["name_kr"]
            print(f'[{label}] {name_val}')
            for r in res[:8]:
                weight_val = r["w"]
                w_str = f"{weight_val:.2f}" if isinstance(weight_val, float) else str(weight_val)
                print(f'  {r["name"]} | {r["rel"]} | w={w_str}')
        else:
            print(f'[{label}] 없음')
        print()

driver.close()
