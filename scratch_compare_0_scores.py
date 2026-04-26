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

zero_queries = []
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
    zero_queries.append((q, relevant, seniority, matched[:5]))

for q, relevant, seniority, top5 in zero_queries:
    print(f'\n[쿼리] {q}')

    # 기존 정답자
    print('  [기존 정답]')
    for rid in list(relevant)[:2]:
        cur.execute('''
            SELECT name_kr, total_years, sector, profile_summary
            FROM candidates WHERE id=?
        ''', (rid,))
        row = cur.fetchone()
        if row:
            print(f'    {row["name_kr"]} | {row["total_years"]}년 | {row["sector"]}')
            print(f'    {str(row["profile_summary"] or "")[:80]}')

    # 현재 1~3위
    print('  [현재 상위 3명]')
    for c in top5[:3]:
        cid = c.get('id')
        cur.execute('''
            SELECT name_kr, total_years, sector, profile_summary
            FROM candidates WHERE id=?
        ''', (cid,))
        row = cur.fetchone()
        if row:
            print(f'    {row["name_kr"]} | {row["total_years"]}년 | {row["sector"]} | score={c.get("score",0):.1f}')
            print(f'    {str(row["profile_summary"] or "")[:80]}')

conn.close()
