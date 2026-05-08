import sys, json, os
sys.stdout.reconfigure(encoding='utf-8')

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT_DIR)

from jd_compiler import api_search_v9

for query, target in [('Enterprise Sales Manager', '최우성'), ('AI Cloud Engineer', '정윤오')]:
    res = api_search_v9(prompt=query, seniority='All')
    candidates = res.get('matched', [])
    rank = None
    for i, c in enumerate(candidates[:50]):
        if c.get('name_kr') == target:
            rank = i+1
            v = c.get('vector_score',0)
            g = c.get('graph_score',0)
            final = c.get('final_score',0)
            print(f'[{query}] {target} -> {rank}위  FINAL:{final:.3f} V:{v:.3f} G:{g:.3f}')
            break
    if not rank:
        print(f'[{query}] {target} -> 50위권 밖')
    
    # 1위 후보자 정보도
    if candidates:
        top = candidates[0]
        print(f'  1위: {top.get("name_kr")} FINAL:{top.get("final_score",0):.3f} V:{top.get("vector_score",0):.3f} G:{top.get("graph_score",0):.3f}')
    print()
