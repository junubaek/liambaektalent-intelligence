import json, sqlite3, sys, time
sys.stdout.reconfigure(encoding='utf-8')
from openai import OpenAI
from neo4j import GraphDatabase
from ontology_graph import CANONICAL_MAP

# Pre-lowercase keys for speed
CANONICAL_LOWER = {k.lower(): v for k, v in CANONICAL_MAP.items() if len(k) > 2}

def build_emb_text(row):
    import json, math, os
    name = row['name_kr'] or ''
    sector = row['sector'] or ''
    summary = row['profile_summary'] or ''
    raw = row['raw_text'] or ''

    # node_idf.json 로드 (캐시)
    if not hasattr(build_emb_text, '_idf'):
        idf_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'node_idf.json')
        build_emb_text._idf = json.load(open(idf_path, encoding='utf-8')) if os.path.exists(idf_path) else {}

    # 약어 풀네임 확장
    ABBR_EXPAND = {
        'HBM': 'HBM(High Bandwidth Memory)',
        'CXL': 'CXL(Compute Express Link)',
        'LLM': 'LLM(Large Language Model)',
        'IPO': 'IPO(기업공개)',
        'M&A': 'M&A(인수합병)',
        'SoC': 'SoC(System on Chip)',
        'MLOps': 'MLOps(머신러닝 운영)',
        'DCF': 'DCF(현금흐름할인법)',
        'RDMA': 'RDMA(원격직접메모리접근)',
    }
    expanded_raw = raw
    for abbr, full in ABBR_EXPAND.items():
        expanded_raw = expanded_raw.replace(abbr, full)

    # 이 후보자의 노드 추출 + IDF 점수
    raw_lower = expanded_raw.lower()
    node_scores = {}
    for src, tgt in CANONICAL_LOWER.items():
        if src in raw_lower:
            node_scores[tgt] = build_emb_text._idf.get(tgt, 0)

    # IDF 상위 5개
    top5 = sorted(node_scores, key=lambda x: -node_scores[x])[:5]
    top5_block = ' '.join(top5) if top5 else ''

    # [NEW] Heuristic: Clean raw_text to focus on career/experience
    lines = expanded_raw.split('\n')
    cleaned_lines = []
    noise_keywords = ['대학교', '대학원', '고등학교', '병역', '군필', '육군', '해군', '공군', '생년월일', '거주지', '주소']
    career_start_keywords = ['경력', '주요 업무', 'Career', 'Experience', '이력사항', 'Work History']
    
    career_started = False
    for line in lines:
        line_s = line.strip()
        if not line_s: continue
        
        # Check if career section starts
        if any(kw in line_s for kw in career_start_keywords):
            career_started = True
            
        # Filter noise
        if any(nk in line_s for nk in noise_keywords):
            continue
            
        # If career started, keep more aggressively
        cleaned_lines.append(line_s)

    final_raw = '\n'.join(cleaned_lines)
    
    parts = [f'{name} {sector}']
    if top5_block:
        parts.append(top5_block)
    if summary:
        parts.append(summary)
        parts.append(summary) # Double weight for summary
    
    # Append cleaned raw text (up to 800 chars)
    parts.append(final_raw[:800])

    return '\n'.join(parts)

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

    # Get ALL IDs for re-embedding
    with driver.session() as s:
        res = s.run('MATCH (c:Candidate) RETURN c.id as id').data()
        ids = [r['id'] for r in res]

    print(f'Embedding update target (All): {len(ids)} candidates')

    BATCH = 50
    done = 0

    for i in range(0, len(ids), BATCH):
        batch_ids = ids[i:i+BATCH]
        
        # Get data from SQLite with seniority CASE
        placeholders = ','.join(['?'] * len(batch_ids))
        query = f'''
            SELECT id, name_kr, sector, profile_summary, raw_text, current_company, total_years,
                   CASE
                     WHEN total_years >= 10 THEN "SENIOR"
                     WHEN total_years >= 5 THEN "MIDDLE"
                     ELSE "JUNIOR"
                   END as seniority
            FROM candidates 
            WHERE id IN ({placeholders})
        '''
        cur.execute(query, batch_ids)
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
