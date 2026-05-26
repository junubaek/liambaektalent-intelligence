import sys, os, json
sys.stdout.reconfigure(encoding='utf-8')
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT_DIR)
os.chdir(ROOT_DIR)

from neo4j import GraphDatabase
from openai import OpenAI

target_id = 'db752f0f-0f1a-437c-a09d-43c20442ab7b'
prompt = "General Affairs Manager"

secrets = json.load(open('secrets.json'))
client = OpenAI(api_key=secrets['OPENAI_API_KEY'])
driver = GraphDatabase.driver(secrets['NEO4J_URI'], auth=(secrets['NEO4J_USERNAME'], secrets['NEO4J_PASSWORD']))

# 1. Get query vector
emb_res = client.embeddings.create(input=[prompt], model="text-embedding-3-small")
query_vector = emb_res.data[0].embedding

# 2. Run vector search in Neo4j
with driver.session() as session:
    res = session.run("""
        CALL db.index.vector.queryNodes('candidate_embedding', 300, $queryVector)
        YIELD node AS c, score
        RETURN c.id AS id, coalesce(c.name_kr, c.name) AS name, score
    """, queryVector=query_vector)
    
    found = False
    for i, r in enumerate(res):
        if r['id'] == target_id:
            print(f"Found Lee Sang-heon in Vector Tower at rank {i+1} with score {r['score']}")
            found = True
            break
    
    if not found:
        print("Lee Sang-heon NOT in top 300 vectors.")

driver.close()
