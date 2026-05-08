import json, sys, os
sys.stdout.reconfigure(encoding='utf-8')

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT_DIR)

from connectors.pinecone_api import PineconeClient
from openai import OpenAI
import sqlite3

secrets = json.load(open(os.path.join(ROOT_DIR, 'secrets.json'), encoding='utf-8'))
openai_client = OpenAI(api_key=secrets.get('OPENAI_API_KEY',''))
pc_host = secrets.get('PINECONE_HOST','').rstrip('/')
if not pc_host.startswith('https://'):
    pc_host = f'https://{pc_host}'
pc = PineconeClient(secrets.get('PINECONE_API_KEY',''), pc_host)

conn = sqlite3.connect(os.path.join(ROOT_DIR, 'candidates.db'))
cur = conn.cursor()
cur.execute('SELECT id FROM candidates WHERE name_kr = "최우성" AND is_duplicate = 0')
cid = cur.fetchone()[0]
conn.close()
print(f'최우성 ID: {cid}')

# 1. Pinecone에 실제로 있는지 fetch
result = pc.fetch(ids=[f'{cid}_chunk_0'], namespace='resume_vectors')
vectors = result.get('vectors', {})
print(f'Pinecone fetch 결과: {list(vectors.keys())}')

# 2. 실제 쿼리로 검색해서 최우성 나오는지
emb = openai_client.embeddings.create(
    model='text-embedding-3-small',
    input=['Enterprise Sales Manager B2B']
).data[0].embedding

search_result = pc.query(
    vector=emb,
    top_k=100,
    namespace='resume_vectors'
)
matches = search_result.get('matches', [])
print(f'Pinecone 검색 결과 수: {len(matches)}')

# 최우성 ID가 포함된 결과 찾기
found = [m for m in matches if cid in str(m.get('metadata', {}).get('candidate_id', ''))]
print(f'최우성 포함 여부: {len(found)}개')
if found:
    print(f'  점수: {found[0]["score"]}')
else:
    print('  ❌ 검색 결과에 없음')
    # 상위 5개 candidate_id 출력
    print('  상위 5개:')
    for m in matches[:5]:
        print(f'    {m.get("metadata", {}).get("candidate_id","?")} score:{m["score"]:.3f}')
