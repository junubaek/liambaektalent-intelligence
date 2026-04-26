import json, math, sys
sys.stdout.reconfigure(encoding='utf-8')
from jd_compiler import api_search_v9

d = json.load(open('golden_dataset_v3.json', encoding='utf-8'))

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

scores = []
for q, info in query_targets.items():
    relevant = info['relevant']
    if not relevant: continue
    # Use v9
    from jd_compiler import api_search_v9
    r = api_search_v9(q, seniority=info['seniority'])
    matched = r.get('matched', [])
    # Matching by ID or Name (since legacy IDs might be mixed)
    dcg = sum(1/math.log2(i+2) for i,c in enumerate(matched[:10]) if str(c.get('id')) in relevant or str(c.get('candidate_id')) in relevant or c.get('name_kr') in relevant)
    idcg = sum(1/math.log2(i+2) for i in range(min(len(relevant),10)))
    scores.append(dcg/idcg if idcg > 0 else 0)

total = sum(scores)/len(scores)
perfect = sum(1 for s in scores if s==1)
zero = sum(1 for s in scores if s==0)
print(f'NDCG@10: {total:.4f}')
print(f'만점: {perfect}개 / 0점: {zero}개')
print(f'초기 대비: +{(total/0.0388-1)*100:.0f}%')
