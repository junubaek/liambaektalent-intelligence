import json
import sys
import os
from neo4j import GraphDatabase

# Ensure project root is in path
sys.path.insert(0, os.getcwd())
from jd_compiler import _get_secret

# Ensure UTF-8 output
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

n_uri = _get_secret('NEO4J_URI')
n_user = _get_secret('NEO4J_USERNAME')
n_pw = _get_secret('NEO4J_PASSWORD')
driver = GraphDatabase.driver(n_uri, auth=(n_user, n_pw))

target_name = '최우성'

with driver.session() as session:
    res = session.run("""
        MATCH (c:Candidate)
        WHERE c.name_kr = $name
        RETURN count(c) as cnt, collect(id(c)) as neo4j_internal_ids, collect(c.id) as uuids, collect(c.embedding IS NOT NULL) as embs
    """, name=target_name).data()
    
    print(f"--- Duplicate Check for '{target_name}' ---")
    if res:
        print(f"Count: {res[0]['cnt']}")
        for i in range(res[0]['cnt']):
            print(f"Node {i+1}: Internal ID: {res[0]['neo4j_internal_ids'][i]} | UUID: {res[0]['uuids'][i]} | Has Embedding: {res[0]['embs'][i]}")
    else:
        print("No nodes found.")

driver.close()
