import json
import os
import sys
from neo4j import GraphDatabase

sys.stdout.reconfigure(encoding='utf-8')

def _get_secret(key):
    try:
        with open('secrets.json', 'r', encoding='utf-8') as f:
            s = json.load(f)
        return s.get(key)
    except:
        return None

driver = GraphDatabase.driver(_get_secret('NEO4J_URI'), auth=(_get_secret('NEO4J_USERNAME'), _get_secret('NEO4J_PASSWORD')))
target_ids = {
    '김영인': '31f22567-1b6f-814b-a3d5-db5c0e51ac2f',
    '김대중': '32e22567-1b6f-81c3-a567-fa97777d7f53',
    '김완희': '31f22567-1b6f-817a-a763-f718d9d40fbf'
}

final_nodes = {}

try:
    with driver.session() as session:
        for name, cid in target_ids.items():
            q = """
            MATCH (c:Candidate)-[r]->(s:Skill)
            WHERE c.id = $cid
            RETURN s.name AS skill, type(r) AS action
            """
            res = session.run(q, cid=cid)
            skills = []
            for r in res:
                skills.append({'skill': r['skill'], 'action': r['action']})
            final_nodes[name] = {
                'id': cid,
                'skills': skills
            }
finally:
    driver.close()

with open('v7_star_nodes.json', 'w', encoding='utf-8') as f:
    json.dump(final_nodes, f, ensure_ascii=False, indent=4)

print("Star nodes extracted successfully.")
