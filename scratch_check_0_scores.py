import json, math, sys, sqlite3
sys.stdout.reconfigure(encoding='utf-8')
from jd_compiler import api_search_v8

d = json.load(open('golden_dataset_v3.json', encoding='utf-8'))
conn = sqlite3.connect('candidates.db')
conn.row_factory = sqlite3.Row
cur = conn.cursor()

query_targets = {}
for item in d:
    q = item.get('query') or item.get('jd_query')
    if not q: continue
    rel = item.get('relevant_ids') or []
    if not rel and item.get('candidate_neo4j_id'):
        rel = [item.get('candidate_neo4j_id')]
    if q not in query_targets:
        query_targets[q] = {
            'relevant': set(),
            'seniority': item.get('seniority','All')
        }
    for r in rel:
        query_targets[q]['relevant'].add(r)

for q, info in query_targets.items():
    relevant = info['relevant']
    seniority = info['seniority']
    if not relevant: continue
    r = api_search_v8(q, seniority=seniority)
    matched = r.get('matched', [])
    dcg = sum(1/math.log2(i+2) for i,c in enumerate(matched[:10]) if c.get('id') in relevant)
    idcg = sum(1/math.log2(i+2) for i in range(min(len(relevant),10)))
    ndcg = dcg/idcg if idcg > 0 else 0
    if ndcg > 0: continue

    print(f'\n[쿼리] {q[:70]}')
    print(f'[Seniority] {seniority}')
    for rid in list(relevant)[:2]:
        cur.execute('''
            SELECT name_kr, total_years, sector,
                   is_pinecone_synced, is_neo4j_synced,
                   profile_summary
            FROM candidates WHERE id=?
        ''', (rid,))
        row = cur.fetchone()
        if row:
            print(f'  정답: {row["name_kr"]} | {row["total_years"]}년 | {row["sector"]}')
            print(f'        pinecone={row["is_pinecone_synced"]} neo4j={row["is_neo4j_synced"]}')
            print(f'        {str(row["profile_summary"] or "")[:80]}')
        else:
            print(f'  정답 ID {rid} → DB 없음')
    if matched:
        print(f'  실제 1위: {matched[0].get("name_kr","?")} | score={matched[0].get("score",0):.1f}')

conn.close()
