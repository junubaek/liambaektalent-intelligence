import json, sqlite3, sys, time
sys.stdout.reconfigure(encoding='utf-8')
from openai import OpenAI
from neo4j import GraphDatabase
from ontology_graph import CANONICAL_MAP

# Pre-lowercase keys for speed
CANONICAL_LOWER = {k.lower(): v for k, v in CANONICAL_MAP.items() if len(k) > 2}

def build_emb_text(row):
    name = row['name_kr'] or ''
    sector = row['sector'] or ''
    summary = row['profile_summary'] or ''
    raw = row['raw_text'] or ''
    
    # Hidden Keyword Block
    kw_set = set()
    raw_lower = raw.lower()
    for src_lower, tgt in CANONICAL_LOWER.items():
        if src_lower in raw_lower:
            kw_set.add(tgt)
    kw_block = '[Keywords: ' + ' '.join(list(kw_set)[:30]) + ']'
    
    return f'{name} {sector}\n{summary}\n{raw[:600]}\n{kw_block}'

def run():
    with open('secrets.json', 'r', encoding='utf-8') as f:
        secrets = json.load(f)
    oai = OpenAI(api_key=secrets['OPENAI_API_KEY'])
    driver = GraphDatabase.driver(
        secrets['NEO4J_URI'],
        auth=(secrets['NEO4J_USERNAME'], secrets['NEO4J_PASSWORD'])
    )

    conn = sqlite3.connect('candidates.db')
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    # Get IDs of candidates missing embedding in Neo4j
    with driver.session() as s:
        res = s.run('MATCH (c:Candidate) WHERE c.embedding IS NULL RETURN c.id as id').data()
        ids = [r['id'] for r in res]

    print(f'Embedding update target: {len(ids)} candidates')

    BATCH = 50
    done = 0

    for i in range(0, len(ids), BATCH):
        batch_ids = ids[i:i+BATCH]
        
        # Get data from SQLite
        placeholders = ','.join(['?'] * len(batch_ids))
        cur.execute(f'SELECT id, name_kr, sector, profile_summary, raw_text FROM candidates WHERE id IN ({placeholders})', batch_ids)
        rows_data = {r['id']: r for r in cur.fetchall()}
        
        texts = []
        valid_ids = []
        for cid in batch_ids:
            row = rows_data.get(cid)
            if row:
                texts.append(build_emb_text(row))
                valid_ids.append(cid)
        
        if not texts:
            continue
        
        # Embed
        resp = oai.embeddings.create(model='text-embedding-3-small', input=texts)
        
        # Update Neo4j
        with driver.session() as s:
            # Using a single query with unwind for efficiency
            params = []
            for j, cid in enumerate(valid_ids):
                params.append({'id': cid, 'emb': resp.data[j].embedding})
            
            s.run('''
                UNWIND $batch as item
                MATCH (c:Candidate {id: item.id})
                SET c.embedding = item.emb
            ''', batch=params)
        
        done += len(valid_ids)
        print(f'  Progress: {done}/{len(ids)}')
        time.sleep(0.1)

    print(f'\nEmbedding update complete: {done} candidates')
    
    # Final check
    with driver.session() as s:
        final_count = s.run('MATCH (c:Candidate) WHERE c.embedding IS NOT NULL RETURN count(c) as n').single()['n']
        print(f'Total candidates with embedding: {final_count}')

    conn.close()
    driver.close()

if __name__ == '__main__':
    run()
