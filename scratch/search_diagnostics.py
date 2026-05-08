import sys, json, os
sys.stdout.reconfigure(encoding='utf-8')

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT_DIR)

from jd_compiler import api_search_v9

def check_search(query, target_name):
    res = api_search_v9(prompt=query, seniority='All')
    candidates = res.get('matched', [])
    print(f'=== {query} 상위 15 ===')
    found = False
    for i, c in enumerate(candidates[:20]): # Show up to 20 to see if it's just outside top 15
        name = c.get('name_kr','?')
        final = c.get('final_score',0)
        v = c.get('vector_score',0)
        g = c.get('graph_score',0)
        marker = ' ← 정답' if name == target_name else ''
        if name == target_name: found = True
        if i < 15 or name == target_name:
            print(f'{i+1:2d}. {name:10s} FINAL:{final:.3f} V:{v:.3f} G:{g:.3f}{marker}')
    if not found:
        print(f'  ❌ {target_name} not found in top 20')
    print()

check_search('Enterprise Sales Manager', '최우성')
check_search('AI Cloud Engineer', '정윤오')
