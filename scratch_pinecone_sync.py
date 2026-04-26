import sqlite3, os, sys, json
sys.stdout.reconfigure(encoding='utf-8')
from openai import OpenAI
from ontology_graph import CANONICAL_MAP

with open("secrets.json", "r", encoding="utf-8") as f:
    secrets = json.load(f)

pc_host = secrets.get("PINECONE_HOST", "").rstrip("/")
if not pc_host.startswith("https://"): pc_host = f"https://{pc_host}"

from connectors.pinecone_api import PineconeClient
pinecone_client = PineconeClient(secrets.get("PINECONE_API_KEY", ""), pc_host)

oai = OpenAI(api_key=secrets.get('OPENAI_API_KEY'))

conn = sqlite3.connect('candidates.db')
conn.row_factory = sqlite3.Row
cur = conn.cursor()

# 최근 재파싱된 후보자 raw_text 재임베딩
cur.execute('''
    SELECT id, name_kr, raw_text, profile_summary, sector
    FROM candidates
    WHERE is_duplicate=0
    AND is_pinecone_synced=1
    AND profile_summary IS NOT NULL
    AND profile_summary != ''
    ORDER BY ROWID DESC
    LIMIT 200
''')
rows = cur.fetchall()
print(f'Pinecone 재임베딩 대상: {len(rows)}명')

def build_chunk_with_keywords(raw_text, name, sector):
    chunk = raw_text[:1000] if raw_text else ''
    keywords = []
    for src, tgt in CANONICAL_MAP.items():
        if src.lower() in (raw_text or '').lower():
            keywords.append(tgt)
    kw_block = ' '.join(set(keywords))[:300]
    return f'{name} {sector or ""} {chunk}\n[Keywords: {kw_block}]'

updated = 0
batch_texts = []
batch_ids = []

for r in rows:
    text = build_chunk_with_keywords(
        r['raw_text'], r['name_kr'], r['sector']
    )
    batch_texts.append(text)
    batch_ids.append(r['id'])
    
    if len(batch_texts) >= 20:
        resp = oai.embeddings.create(
            model='text-embedding-3-small',
            input=batch_texts
        )
        vectors = [{"id": f"{bid}_chunk_0", "values": emb.embedding, "metadata": {'candidate_id': bid, 'chunk_index': 0}}
                   for bid, emb in zip(batch_ids, [e for e in resp.data])]
        pinecone_client.upsert(vectors=vectors, namespace='resume_vectors')
        updated += len(batch_texts)
        print(f'  {updated}/{len(rows)} 재임베딩 완료')
        batch_texts = []
        batch_ids = []

# 나머지
if batch_texts:
    resp = oai.embeddings.create(
        model='text-embedding-3-small',
        input=batch_texts
    )
    vectors = [{"id": f"{bid}_chunk_0", "values": emb.embedding, "metadata": {'candidate_id': bid, 'chunk_index': 0}}
               for bid, emb in zip(batch_ids, [e for e in resp.data])]
    pinecone_client.upsert(vectors=vectors, namespace='resume_vectors')
    updated += len(batch_texts)

print(f'Pinecone 재임베딩 완료: {updated}명')
conn.close()
