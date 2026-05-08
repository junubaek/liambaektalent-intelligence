import json, sys, os
sys.stdout.reconfigure(encoding='utf-8')

# Root directory check
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT_DIR)

from connectors.pinecone_api import PineconeClient
import sqlite3

secrets = json.load(open(os.path.join(ROOT_DIR, 'secrets.json'), encoding='utf-8'))
pc_host = secrets.get('PINECONE_HOST','').rstrip('/')
if not pc_host.startswith('https://'):
    pc_host = f'https://{pc_host}'
pc = PineconeClient(secrets.get('PINECONE_API_KEY',''), pc_host)

conn = sqlite3.connect(os.path.join(ROOT_DIR, 'candidates.db'))
cur = conn.cursor()

for name in ['최우성', '정윤오', '이상헌']:
    cur.execute('SELECT id FROM candidates WHERE name_kr = ? AND is_duplicate = 0', (name,))
    row = cur.fetchone()
    if not row:
        print(f'[{name}] DB 마스터 없음')
        continue
    cid = row[0]
    
    # Pinecone에서 해당 ID 벡터 조회
    try:
        result = pc.query(vector=[0.0]*1536, top_k=1, filter_meta={'candidate_id': cid}, namespace='resume_vectors')
        matches = result.get('matches', [])
        if matches:
            print(f'[{name}] ✅ Pinecone 벡터 있음 (총 {len(matches)}개 이상의 청크)')
        else:
            # Try fetching by ID too as a fallback
            try:
                fetch_res = pc.fetch(ids=[f'{cid}_chunk_0'], namespace='resume_vectors')
                if fetch_res.get('vectors'):
                    print(f'[{name}] ✅ Pinecone 벡터 있음 (ID 매칭 확인)')
                else:
                    print(f'[{name}] ❌ Pinecone 벡터 없음 → 재임베딩 필요')
            except:
                print(f'[{name}] ❌ Pinecone 벡터 없음 → 재임베딩 필요')
    except Exception as e:
        print(f'[{name}] 오류: {e}')

conn.close()
