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

    # 약어 풀네임 병기 (임베딩 품질 향상)
    ABBR_EXPAND = {
        'HBM': 'HBM(High Bandwidth Memory)',
        'CXL': 'CXL(Compute Express Link)',
        'RAG': 'RAG(Retrieval Augmented Generation)',
        'LLM': 'LLM(Large Language Model)',
        'IPO': 'IPO(기업공개)',
        'M&A': 'M&A(인수합병)',
        'RTL': 'RTL(Register Transfer Level)',
        'DFT': 'DFT(Design for Testability)',
        'SoC': 'SoC(System on Chip)',
        'vLLM': 'vLLM(LLM 추론 최적화)',
        'MLOps': 'MLOps(머신러닝 운영)',
        'DevOps': 'DevOps(개발운영통합)',
        'ESG': 'ESG(환경사회지배구조)',
        'ERP': 'ERP(전사적자원관리)',
        'SCM': 'SCM(공급망관리)',
        'ASRS': 'ASRS(자동창고시스템)',
        'MBO': 'MBO(경영자인수)',
        'DCF': 'DCF(현금흐름할인)',
        'LBO': 'LBO(차입매수)',
        'RDMA': 'RDMA(원격직접메모리접근)',
    }

    # 원문에 약어 풀네임 병기
    expanded_raw = raw
    for abbr, fullname in ABBR_EXPAND.items():
        expanded_raw = expanded_raw.replace(abbr, fullname)

    # Canonical Map → 도메인 카테고리 힌트만 (Graph와 중복 최소화)
    DOMAIN_HINT_MAP = {
        'rtl': 'SEMICONDUCTOR_HW', 'verilog': 'SEMICONDUCTOR_HW',
        'fpga': 'SEMICONDUCTOR_HW', 'asic': 'SEMICONDUCTOR_HW',
        'hbm': 'SEMICONDUCTOR_HW', 'npu': 'SEMICONDUCTOR_HW',
        'pytorch': 'AI_ML', 'tensorflow': 'AI_ML',
        'llm': 'AI_ML', 'transformer': 'AI_ML',
        'rag': 'AI_ML', 'diffusion': 'AI_ML',
        'kubernetes': 'DEVOPS_CLOUD', 'docker': 'DEVOPS_CLOUD',
        'terraform': 'DEVOPS_CLOUD', 'aws': 'DEVOPS_CLOUD',
        'treasury': 'FINANCE_OP', '자금': 'FINANCE_OP',
        'ipo': 'FINANCE_DEAL', 'valuation': 'FINANCE_DEAL',
        'kafka': 'DATA_INFRA', 'spark': 'DATA_INFRA',
        'scm': 'SUPPLY_CHAIN', '물류': 'SUPPLY_CHAIN',
        'blockchain': 'WEB3', 'nft': 'WEB3',
    }
    raw_lower = raw.lower()
    domain_hints = set()
    for kw, domain in DOMAIN_HINT_MAP.items():
        if kw in raw_lower:
            domain_hints.add(domain)

    # 기존 Keywords 블록 유지 (하위 호환성)
    kw_set = set()
    for src_lower, tgt in CANONICAL_LOWER.items():
        if src_lower in raw_lower:
            kw_set.add(tgt)
    kw_block = '[Keywords: ' + ' '.join(list(kw_set)[:30]) + ']'

    # 도메인 힌트 블록
    domain_block = '[Domain: ' + ' '.join(sorted(domain_hints)) + ']' if domain_hints else ''

    # 자연어 형태 유지 + 약어 풀네임 + 원문 800자
    parts = [f'{name} {sector}']
    if summary:
        parts.append(summary)
    parts.append(expanded_raw[:800])
    if domain_block:
        parts.append(domain_block)
    parts.append(kw_block)

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
