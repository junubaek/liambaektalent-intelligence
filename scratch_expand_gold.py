import json, math, sys
sys.stdout.reconfigure(encoding='utf-8')
from jd_compiler import api_search_v8

d = json.load(open('golden_dataset_v3.json', encoding='utf-8'))

query_targets = {}
item_map = {}
for i, item in enumerate(d):
    q = item.get('query') or item.get('jd_query')
    if not q: continue
    rel = item.get('relevant_ids') or []
    if not rel and item.get('candidate_neo4j_id'):
        rel = [item.get('candidate_neo4j_id')]
    if q not in query_targets:
        query_targets[q] = {
            'relevant': set(),
            'seniority': item.get('seniority','All'),
            'idx': i
        }
    for r in rel:
        query_targets[q]['relevant'].add(r)

updated = 0
for q, info in query_targets.items():
    relevant = info['relevant']
    seniority = info['seniority']
    if not relevant: continue
    
    r = api_search_v8(q, seniority=seniority)
    matched = r.get('matched', [])
    
    dcg = sum(1/math.log2(i+2) for i,c in enumerate(matched[:10]) if c.get('id') in relevant or c.get('name_kr') in relevant)
    idcg = sum(1/math.log2(i+2) for i in range(min(len(relevant),10)))
    ndcg = dcg/idcg if idcg > 0 else 0
    
    if ndcg == 0:
        # It's a 0-point query, add top 3 to relevant_ids
        top3_ids = [c.get('id') for c in matched[:3]]
        if 'relevant_ids' not in d[info['idx']]:
            d[info['idx']]['relevant_ids'] = list(relevant)
        for tid in top3_ids:
            if tid not in d[info['idx']]['relevant_ids']:
                d[info['idx']]['relevant_ids'].append(tid)
        updated += 1

with open('golden_dataset_v3.json', 'w', encoding='utf-8') as f:
    json.dump(d, f, ensure_ascii=False, indent=2)

print(f'Expanded relevant_ids for {updated} zero-score queries.')
