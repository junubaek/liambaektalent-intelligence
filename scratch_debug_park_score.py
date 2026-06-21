import json
import sys
from neo4j import GraphDatabase
import openai

sys.stdout.reconfigure(encoding='utf-8')

with open('secrets.json', encoding='utf-8') as f:
    secrets = json.load(f)

openai_client = openai.OpenAI(api_key=secrets['OPENAI_API_KEY'])
res = openai_client.embeddings.create(model='text-embedding-3-small', input=['HPC CUDA parallel computing C++ Rust GPU'])
q_vec = res.data[0].embedding

driver = GraphDatabase.driver(secrets['NEO4J_URI'], auth=(secrets['NEO4J_USERNAME'], secrets['NEO4J_PASSWORD']))
with driver.session() as session:
    res = session.run('''
        CALL db.index.vector.queryNodes('candidate_embedding', 200, $queryVector)
        YIELD node AS c, score
        RETURN c.id AS id, c.name_kr AS name_kr, score
    ''', queryVector=q_vec)
    records = list(res)
    print(f'Total vector matches: {len(records)}')
    for idx, r in enumerate(records[:15]):
        print(f"{idx+1}. {r['name_kr']} ({r['id']}) | score={r['score']}")
        
    print('\nChecking if target ID exists in vector search:')
    target_id = '3d322d13-0699-4453-b70e-5a4c2aac38f9' # 박천혁
    for idx, r in enumerate(records):
        if r['id'] == target_id:
            print(f'  Found {target_id} at rank {idx+1}')
            break
    else:
        print(f'  Target ID {target_id} NOT found in vector search results!')
driver.close()
