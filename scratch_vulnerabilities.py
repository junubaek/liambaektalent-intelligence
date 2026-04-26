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
    
    dcg = 0
    for i, c in enumerate(matched[:10]):
        if c.get('id') in relevant or c.get('name_kr') in relevant:
            dcg += 1 / math.log2(i + 2)
            
    if dcg == 0:
        zero_queries.append({'query': q, 'seniority': seniority, 'expected': list(relevant), 'top3': [c.get('name_kr') for c in matched[:3]]})

print(f'Total 0-point queries: {len(zero_queries)}')
for zq in zero_queries:
    print(f"Q: {zq['query']} ({zq['seniority']}) | Expected: {zq['expected']} | Top3 Returned: {zq['top3']}")

# 빈 Gravity Field 찾기
from ontology_graph import CANONICAL_MAP, UNIFIED_GRAVITY_FIELD
target_nodes = set(CANONICAL_MAP.values())
missing = []
for n in target_nodes:
    if n not in UNIFIED_GRAVITY_FIELD:
        missing.append(n)

print(f'\nTotal Missing Gravity Fields: {len(missing)}')
for m in missing:
    print(f'- {m}')
