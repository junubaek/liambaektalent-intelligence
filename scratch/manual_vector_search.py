import json
from neo4j import GraphDatabase
from openai import OpenAI

secrets = json.load(open('secrets.json'))
driver = GraphDatabase.driver(secrets['NEO4J_URI'], auth=(secrets['NEO4J_USERNAME'], secrets['NEO4J_PASSWORD']))
openai_client = OpenAI(api_key=secrets.get('OPENAI_API_KEY',''))
session = driver.session()

cid = 'c3d4ee55-266a-44f6-8e66-fb7486be38a8'

# 1. 최우성 summary/raw_text 확인
res = session.run('''
    MATCH (c:Candidate {id: $cid})
    RETURN c.profile_summary as summary, c.current_company as current_company, c.sector as sector, c.name as name
''', cid=cid).data()
print('최우성 Neo4j 데이터:')
print(res)
print()

# 2. 쿼리 임베딩으로 직접 Neo4j 벡터 검색
query_emb = openai_client.embeddings.create(
    model='text-embedding-3-small',
    input=['Enterprise Sales Manager B2B 영업']
).data[0].embedding

results = session.run('''
    CALL db.index.vector.queryNodes("candidate_embedding", 50, $vec)
    YIELD node, score
    RETURN node.id as id, coalesce(node.name_kr, node.name) as name, score
    ORDER BY score DESC
''', vec=query_emb).data()

print('Neo4j 벡터 검색 결과 (상위 50 중 타겟 확인):')
found = False
for i, r in enumerate(results):
    marker = ' ← 최우성' if r['name'] == '최우성' else ''
    if r['name'] == '최우성': found = True
    if i < 20 or r['name'] == '최우성':
        print(f'{i+1:2d}. {r["name"]:10s} score:{r["score"]:.4f}{marker}')

if not found:
    print('  ❌ 최우성 not found in top 50 vector results')

driver.close()
