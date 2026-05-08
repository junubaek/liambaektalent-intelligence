import json
import sys
import os
from openai import OpenAI
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

client = OpenAI(api_key=_get_secret('OPENAI_API_KEY'))
query = 'Enterprise Sales Manager'
target_id = 'c3d4ee55-266a-44f6-8e66-fb7486be38a8'

print(f"Checking Raw Vector Score for: '{query}' and Target: {target_id}")
q_vec = client.embeddings.create(input=[query], model='text-embedding-3-small').data[0].embedding

with driver.session() as session:
    # Query more (1000) to find him
    res = session.run("""
        CALL db.index.vector.queryNodes("candidate_embedding", 1000, $q_vec)
        YIELD node, score
        WHERE node.id = $tid
        RETURN node.name_kr as name, score
    """, q_vec=q_vec, tid=target_id).data()
    
    if res:
        print(f"Found: {res[0]['name']} | Vector Score: {res[0]['score']}")
    else:
        print("Target NOT FOUND in Neo4j Vector Index (Top 1000).")
        # Check if node has embedding at all
        res_emb = session.run("MATCH (c:Candidate {id: $tid}) RETURN c.embedding IS NOT NULL as has_emb", tid=target_id).single()
        print(f"Node has embedding: {res_emb['has_emb']}")

driver.close()
