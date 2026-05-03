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

n_uri = _get_secret('NEO4J_URI')
n_user = _get_secret('NEO4J_USERNAME')
n_pw = _get_secret('NEO4J_PASSWORD')

if not all([n_uri, n_user, n_pw]):
    print("Error: Neo4j credentials missing in secrets.json")
    exit(1)

driver = GraphDatabase.driver(n_uri, auth=(n_user, n_pw))
names = ['김영인', '김대중', '김완희']

results = {}

try:
    with driver.session() as session:
        for name in names:
            q = """
            MATCH (c:Candidate)-[r]->(s:Skill)
            WHERE c.name_kr = $name AND c.is_duplicate = 0
            RETURN c.id AS id, c.name_kr AS name, collect(s.name) AS skills
            """
            res = session.run(q, name=name)
            found = False
            for r in res:
                found = True
                results[name] = {
                    'id': str(r['id']),
                    'skills': r['skills']
                }
            if not found:
                print(f"Warning: Candidate {name} not found in Neo4j.")
finally:
    driver.close()

with open('star_candidates_nodes.json', 'w', encoding='utf-8') as f:
    json.dump(results, f, ensure_ascii=False, indent=4)

print("Extraction complete. Results saved to star_candidates_nodes.json")
