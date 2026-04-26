import sqlite3, json, sys, time, os
from openai import OpenAI
from pinecone import Pinecone
from ontology_graph import CANONICAL_MAP

# Set encoding for Windows
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def get_secrets():
    with open('secrets.json', 'r', encoding='utf-8') as f:
        return json.load(f)

# Pre-lowercase keys for faster matching
CANONICAL_ITEMS = [(src.lower(), tgt) for src, tgt in CANONICAL_MAP.items() if len(src) > 2]

def build_chunks(row):
    result = []
    name = row['name_kr'] or ''
    sector = row['sector'] or ''
    raw = row['raw_text'] or ''
    raw_lower = raw.lower() if raw else ''
    
    # Hidden Keyword Block
    kw_set = set()
    for src_lower, tgt in CANONICAL_ITEMS:
        if src_lower in raw_lower:
            kw_set.add(tgt)
    kw_list = list(kw_set)
    kw_block = '[Keywords: ' + ' '.join(kw_list[:30]) + ']'

    # 청크 1: raw_text 앞부분 (학력/스킬/자기소개 포함)
    raw_chunk = f'{name} {sector}\n{raw[:800] if raw else ""}\n{kw_block}'
    result.append((row['id']+'_raw', raw_chunk,
                   {'candidate_id': row['id'], 'chunk_idx': 0}))

    # 청크 2~5: 경력별 (최신 4개)
    try:
        careers = json.loads(row['careers_json'] or '[]')
        if isinstance(careers, dict):
            careers = [careers]
    except:
        careers = []

    for i, c in enumerate(careers[:4]):
        company = c.get('company','') or ''
        title = c.get('title','') or ''
        start = c.get('start_date','') or ''
        end = c.get('end_date','') or '현재'
        desc = c.get('description','') or ''

        # 최신 경력(i=0)에 이름/섹터 반복 (Recency boost)
        boost = f'{name} {sector} ' if i == 0 else ''
        desc_str = str(desc) if desc else ""
        chunk = f'{boost}{title} at {company} ({start}~{end})\n{desc_str[:400]}\n{kw_block}'
        result.append((row['id']+f'_c{i}', chunk,
                       {'candidate_id': row['id'], 'chunk_idx': i+1}))

    return result

def main():
    secrets = get_secrets()
    oai = OpenAI(api_key=secrets['OPENAI_API_KEY'])
    pc = Pinecone(api_key=secrets['PINECONE_API_KEY'])
    index = pc.Index('vector')

    conn = sqlite3.connect('candidates.db')
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute('''
        SELECT id, name_kr, raw_text, careers_json, sector
        FROM candidates WHERE is_duplicate=0
        ORDER BY ROWID
    ''')
    rows = cur.fetchall()
    print(f'Total candidates: {len(rows)}')

    print('Generating chunks...')
    all_chunks = []
    for row in rows:
        try:
            chunks = build_chunks(row)
            all_chunks.extend(chunks)
        except Exception as e:
            print(f"Error building chunks for row {row['id']}: {e}")
            raise e
            
    print(f'Total chunks: {len(all_chunks)}')

    print('Deleting old vectors in namespace resume_vectors...')
    try:
        index.delete(delete_all=True, namespace='resume_vectors')
        time.sleep(3)
        print('Deletion complete')
    except Exception as e:
        print(f"Error deleting vectors: {e}")

    BATCH = 20
    done = 0
    print('Re-embedding started...')
    for i in range(0, len(all_chunks), BATCH):
        batch = all_chunks[i:i+BATCH]
        texts = [c[1] for c in batch]
        ids   = [c[0] for c in batch]
        metas = [c[2] for c in batch]
        
        try:
            resp = oai.embeddings.create(
                model='text-embedding-3-small',
                input=texts
            )
            
            vectors = [(ids[j], resp.data[j].embedding, metas[j])
                       for j in range(len(batch))]
            index.upsert(vectors=vectors, namespace='resume_vectors')
            
            done += len(batch)
            if done % 100 == 0 or done == len(all_chunks):
                print(f'  {done}/{len(all_chunks)} complete')
        except Exception as e:
            print(f"Error at batch {i}: {e}")
            time.sleep(2) # Simple retry logic might be needed but let's just log for now

    print(f'Re-embedding complete: {done} vectors')
    conn.close()

if __name__ == '__main__':
    main()
