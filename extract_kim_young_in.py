import json
import os
from neo4j import GraphDatabase

def _get_secret(key):
    try:
        with open('secrets.json', 'r', encoding='utf-8') as f:
            s = json.load(f)
        return s.get(key)
    except:
        return None

driver = GraphDatabase.driver(_get_secret('NEO4J_URI'), auth=(_get_secret('NEO4J_USERNAME'), _get_secret('NEO4J_PASSWORD')))
other_ids = [
    '32022567-1b6f-81f4-84bc-dbc8d27a4842',
    '04a827ba-635f-4926-bfee-4f5c994acde5',
    '8c24ab94-ce20-4e73-b2bf-a9c05a4ab7e0',
    '31f22567-1b6f-814b-a3d5-db5c0e51ac2f'
]

results = {}
try:
    with driver.session() as session:
        for cid in other_ids:
            q = """
            MATCH (c:Candidate)-[r]->(s:Skill)
            WHERE c.id = $cid
            RETURN c.name_kr AS name, s.name AS skill, type(r) AS action
            """
            res = session.run(q, cid=cid)
            skills = []
            name = 'Unknown'
            for r in res:
                name = r['name']
                skills.append({'skill': r['skill'], 'action': r['action']})
            if skills:
                results[cid] = {'name': name, 'skills': skills}
finally:
    driver.close()

with open('kim_young_in_nodes.json', 'w', encoding='utf-8') as f:
    json.dump(results, f, ensure_ascii=False, indent=4)

print("Kim Young-in skills extracted successfully.")
