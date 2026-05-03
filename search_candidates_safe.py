import json
import os
import sys
from neo4j import GraphDatabase

# Ensure UTF-8 output
sys.stdout.reconfigure(encoding='utf-8')

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

driver = GraphDatabase.driver(n_uri, auth=(n_user, n_pw))
with driver.session() as session:
    # 김영인, 김대중, 김완희
    search_names = ['김영인', '김대중', '김완희']
    for name in search_names:
        print(f"--- Searching for: {name} ---")
        q = """
        MATCH (c:Candidate)
        WHERE c.name_kr CONTAINS $name
        RETURN c.id AS id, c.name_kr AS name_kr, c.name AS name, labels(c) AS labels
        """
        res = session.run(q, name=name)
        found = False
        for r in res:
            found = True
            print(f"Found: ID={r['id']} | NameKR={r['name_kr']} | Name={r['name']}")
        if not found:
            print(f"No results for {name}")

driver.close()
