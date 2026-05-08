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

print(f"Top 20 Vector Results for: '{query}'")
q_vec = client.embeddings.create(input=[query], model='text-embedding-3-small').data[0].embedding

with driver.session() as session:
    res = session.run("""
        CALL db.index.vector.queryNodes("candidate_embedding", 20, $q_vec)
        YIELD node, score
        RETURN node.name_kr as name, node.id as id, score
    """, q_vec=q_vec).data()
    
    for i, r in enumerate(res):
        print(f"Rank {i+1:2d}: {r['name']:10s} | ID: {r['id']} | Score: {r['score']:.4f}")

driver.close()
