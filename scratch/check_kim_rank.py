import json, os
from neo4j import GraphDatabase
from openai import OpenAI

secrets = json.load(open('secrets.json'))
driver = GraphDatabase.driver(secrets['NEO4J_URI'], auth=(secrets['NEO4J_USERNAME'], secrets['NEO4J_PASSWORD']))
openai_client = OpenAI(api_key=secrets.get('OPENAI_API_KEY',''))
session = driver.session()

query = 'Treasury Manager'
target_name = '김대중'

# 쿼리 임베딩
query_emb = openai_client.embeddings.create(
    model='text-embedding-3-small',
    input=[query]
).data[0].embedding

results = session.run('''
    CALL db.index.vector.queryNodes("candidate_embedding", 100, $vec)
    YIELD node, score
    RETURN node.id as id, coalesce(node.name_kr, node.name) as name, score
    ORDER BY score DESC
''', vec=query_emb).data()

print(f'=== {query} Neo4j 벡터 검색 결과 (상위 100) ===')
found = False
for i, r in enumerate(results):
    name = r['name']
    score = r['score']
    marker = f' ← {target_name}' if name == target_name else ''
    if name == target_name:
        found = True
        print(f'{i+1:2d}. {name:10s} score:{score:.4f}{marker}')
    elif i < 15:
        print(f'{i+1:2d}. {name:10s} score:{score:.4f}')

if not found:
    print(f'  ❌ {target_name} not found in top 100')

driver.close()
