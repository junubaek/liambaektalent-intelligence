import sqlite3, sys, os, json, time, datetime
import google.generativeai as genai
from concurrent.futures import ThreadPoolExecutor, as_completed
sys.stdout.reconfigure(encoding='utf-8')

# 1. Credentials
with open('secrets.json', 'r', encoding='utf-8') as f:
    secrets = json.load(f)

genai.configure(api_key=secrets.get('GEMINI_API_KEY'))
model = genai.GenerativeModel('gemini-2.5-flash')

from neo4j import GraphDatabase
uri = secrets.get('NEO4J_URI', 'neo4j+s://72de4959.databases.neo4j.io')
user = secrets.get('NEO4J_USERNAME', 'neo4j')
pw = secrets.get('NEO4J_PASSWORD')
neo_driver = GraphDatabase.driver(uri, auth=(user, pw))

pc_host = secrets.get("PINECONE_HOST", "").rstrip("/")
if not pc_host.startswith("https://"): pc_host = f"https://{pc_host}"
from connectors.pinecone_api import PineconeClient
pinecone_client = PineconeClient(secrets.get("PINECONE_API_KEY", ""), pc_host)
from openai import OpenAI
oai = OpenAI(api_key=secrets.get('OPENAI_API_KEY'))
from ontology_graph import CANONICAL_MAP

# 2. Extract targets
conn = sqlite3.connect('candidates.db')
conn.row_factory = sqlite3.Row
cur = conn.cursor()
cur.execute('''
    SELECT id, name_kr, raw_text, google_drive_url, sector, profile_summary
    FROM candidates
    WHERE is_duplicate=0
    AND (
        profile_summary IS NULL OR profile_summary = ''
        OR sector IS NULL OR sector = ''
        OR sector = '미분류'
    )
    ORDER BY ROWID
''')
targets = cur.fetchall()
print(f'전체 재파싱 대상: {len(targets)}명')
conn.close()

def parse_target(row):
    cid = row['id']
    name = row['name_kr'] or '이름없음'
    raw = (row['raw_text'] or '')[:3000]
    
    if len(raw) < 50:
        return cid, False, "", "", 0

    prompt = f'''아래 이력서에서 추출해줘. JSON만 반환.

이력서:
{raw}

추출 항목:
- profile_summary: 핵심역량 2문장 (한글, 개인정보 제외)
- sector: 주요 직군 (SW/Finance/HR/Marketing/Strategy/Operations/Legal/Semiconductor/Healthcare/Education 중 하나)
- total_years: 총 경력연수 (숫자만)

JSON 형식:
{{"profile_summary": "...", "sector": "...", "total_years": 0}}'''

    for attempt in range(3):
        try:
            resp = model.generate_content(prompt)
            text = resp.text.strip()
            if text.startswith('```'):
                text = text.split('```')[1]
                if text.startswith('json'):
                    text = text[4:]
            parsed = json.loads(text.strip())
            summary = parsed.get('profile_summary', '')
            sector = parsed.get('sector', '')
            years = parsed.get('total_years', 0)
            return cid, True, summary, sector, years
        except Exception as e:
            time.sleep(2)
    return cid, False, "", "", 0

def sync_batch_to_neo4j_pinecone(batch_cids):
    conn = sqlite3.connect('candidates.db')
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    
    placeholders = ','.join(['?']*len(batch_cids))
    cur.execute(f'''
        SELECT id, name_kr, raw_text, profile_summary, sector, total_years
        FROM candidates
        WHERE id IN ({placeholders})
    ''', batch_cids)
    rows = cur.fetchall()
    conn.close()
    
    # Neo4j Sync
    updated_neo = 0
    with neo_driver.session() as s:
        for r in rows:
            s.run('''
                MATCH (c:Candidate {id: $id})
                SET c.sector = $sector,
                    c.profile_summary = $summary,
                    c.total_years = $total_years
            ''', id=r['id'], sector=r['sector'] or '', summary=r['profile_summary'], total_years=r['total_years'])
            updated_neo += 1
    print(f'  [Sync] Neo4j 업데이트 완료: {updated_neo}명')

    # Pinecone Sync
    def build_chunk_with_keywords(raw_text, name, sector):
        chunk = raw_text[:1000] if raw_text else ''
        keywords = []
        for src, tgt in CANONICAL_MAP.items():
            if src.lower() in (raw_text or '').lower():
                keywords.append(tgt)
        kw_block = ' '.join(set(keywords))[:300]
        return f'{name} {sector or ""} {chunk}\\n[Keywords: {kw_block}]'

    batch_texts = []
    batch_ids = []
    updated_pc = 0
    
    for r in rows:
        text = build_chunk_with_keywords(r['raw_text'], r['name_kr'], r['sector'])
        batch_texts.append(text)
        batch_ids.append(r['id'])
        
        if len(batch_texts) >= 20:
            resp = oai.embeddings.create(model='text-embedding-3-small', input=batch_texts)
            vectors = [{"id": f"{bid}_chunk_0", "values": emb.embedding, "metadata": {'candidate_id': bid, 'chunk_index': 0}}
                       for bid, emb in zip(batch_ids, [e for e in resp.data])]
            pinecone_client.upsert(vectors=vectors, namespace='resume_vectors')
            updated_pc += len(batch_texts)
            batch_texts = []
            batch_ids = []
            
    if batch_texts:
        resp = oai.embeddings.create(model='text-embedding-3-small', input=batch_texts)
        vectors = [{"id": f"{bid}_chunk_0", "values": emb.embedding, "metadata": {'candidate_id': bid, 'chunk_index': 0}}
                   for bid, emb in zip(batch_ids, [e for e in resp.data])]
        pinecone_client.upsert(vectors=vectors, namespace='resume_vectors')
        updated_pc += len(batch_texts)
    print(f'  [Sync] Pinecone 재임베딩 완료: {updated_pc}명')

total_done = 0
total_fixed = 0
unsynced_cids = []

BATCH = 50
for i in range(0, len(targets), BATCH):
    batch = targets[i:i+BATCH]
    results = []
    with ThreadPoolExecutor(max_workers=20) as executor:
        futures = {executor.submit(parse_target, row): row for row in batch}
        for future in as_completed(futures):
            results.append(future.result())
            
    conn = sqlite3.connect('candidates.db')
    cur = conn.cursor()
    for cid, ok, summary, sector, years in results:
        if ok and (summary or sector):
            cur.execute('''
                UPDATE candidates
                SET profile_summary=?,
                    sector=CASE WHEN sector IS NULL OR sector='' OR sector='미분류'
                           THEN ? ELSE sector END,
                    total_years=CASE WHEN total_years IS NULL OR total_years=0
                                THEN ? ELSE total_years END
                WHERE id=?
            ''', (summary, sector, years, cid))
            total_fixed += 1
            unsynced_cids.append(cid)
    conn.commit()
    conn.close()
    
    total_done += len(batch)
    print(f'진행: {total_done}/{len(targets)}명 처리 | 누적 수정: {total_fixed}명')
    
    if len(unsynced_cids) >= 500:
        print(f'-> 500명 도달. 동기화 실행 중...')
        sync_batch_to_neo4j_pinecone(unsynced_cids)
        unsynced_cids = []

if unsynced_cids:
    print(f'-> 잔여 데이터 동기화 실행 중...')
    sync_batch_to_neo4j_pinecone(unsynced_cids)
    unsynced_cids = []

neo_driver.close()

# 최종 현황
conn = sqlite3.connect('candidates.db')
cur = conn.cursor()
cur.execute('''
    SELECT COUNT(*) FROM candidates
    WHERE is_duplicate=0
    AND (profile_summary IS NULL OR profile_summary = ''
    OR sector IS NULL OR sector = '' OR sector = '미분류')
''')
remaining = cur.fetchone()[0]
print(f'\\n완료! 남은 미파싱: {remaining}명')
print(f'총 수정: {total_fixed}명')
conn.close()

# Evaluate NDCG
import math
from jd_compiler import api_search_v8

print("\\n=== NDCG 최종 재측정 ===")
d = json.load(open('golden_dataset_v3.json', encoding='utf-8'))
query_targets = {}
for item in d:
    q = item.get('query') or item.get('jd_query')
    if not q: continue
    rel = item.get('relevant_ids') or []
    if not rel and item.get('candidate_neo4j_id'):
        rel = [item.get('candidate_neo4j_id')]
    if q not in query_targets:
        query_targets[q] = {'relevant': set(), 'seniority': item.get('seniority','All')}
    for r in rel:
        query_targets[q]['relevant'].add(r)

scores = []
zero_count = 0
perfect_count = 0

for q, info in query_targets.items():
    relevant = info['relevant']
    seniority = info['seniority']
    if not relevant: continue
    r = api_search_v8(q, seniority=seniority)
    matched = r.get('matched', [])
    dcg = sum(1/math.log2(i+2) for i,c in enumerate(matched[:10]) if c.get('id') in relevant)
    idcg = sum(1/math.log2(i+2) for i in range(min(len(relevant),10)))
    ndcg = dcg/idcg if idcg > 0 else 0
    scores.append(ndcg)
    if ndcg == 0: zero_count += 1
    if ndcg == 1: perfect_count += 1

total = sum(scores)/len(scores)
print(f'전체 NDCG@10:  {total:.4f}')
print(f'0점 쿼리:      {zero_count}개')
print(f'만점 쿼리:     {perfect_count}개')
print(f'초기 대비:     +{(total/0.0388-1)*100:.0f}%')

# Upload to Google Drive
from connectors.gdrive_api import GDriveConnector
from googleapiclient.http import MediaFileUpload

print("\\n=== Google Drive 업로드 ===")
gdrive = GDriveConnector()
folder_id = secrets.get('GOOGLE_DRIVE_FOLDER_ID')
media = MediaFileUpload('candidates.db', resumable=True)
name = f"candidates_reparsed_{datetime.datetime.now().strftime('%Y%m%d_%H%M')}.db"
gdrive.service.files().create(body={'name': name, 'parents': [folder_id]}, media_body=media).execute()
print(f'Upload complete: {name}')
