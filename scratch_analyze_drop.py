import json, math, sys
sys.stdout.reconfigure(encoding='utf-8')
from jd_compiler import api_search_v8

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

results = []
for q, info in query_targets.items():
    relevant = info['relevant']
    if not relevant: continue
    r = api_search_v8(q, seniority=info['seniority'])
    matched = r.get('matched', [])
    dcg = sum(1/math.log2(i+2) for i,c in enumerate(matched[:10]) if c.get('id') in relevant or c.get('name_kr') in relevant)
    idcg = sum(1/math.log2(i+2) for i in range(min(len(relevant),10)))
    ndcg = dcg/idcg if idcg > 0 else 0
    results.append((ndcg, q[:60], info['seniority']))

results.sort()
print('=== 하위 쿼리 (하락한 것들) ===')
for score, q, s in results[:10]:
    print(f'  {score:.4f} [{s}] {q}')
print()
print('=== 상위 쿼리 ===')
for score, q, s in results[-5:]:
    print(f'  {score:.4f} [{s}] {q}')

from ontology_graph import UNIFIED_GRAVITY_FIELD
print('\n=== 자동 생성 중력장 샘플 ===')
check_nodes = [
    'Android_Development',
    'Data_Analysis', 
    'Information_Security',
    'Mobile_Application_Development',
    'Performance_Marketing',
    'Digital_Marketing',
    'Java',
    'Python',
]

for node in check_nodes:
    field = UNIFIED_GRAVITY_FIELD.get(node, {})
    core = field.get('core_attracts', {})
    rep = field.get('repels', {})
    print(f'[{node}]')
    print(f'  core: {core}')
    print(f'  repels: {rep}')
    print()
