import sys, os, json
sys.path.append(os.getcwd())
sys.stdout.reconfigure(encoding='utf-8')
from jd_compiler import api_search_v9

res = api_search_v9(prompt='DevOps Engineer', seniority='All')
matched = res.get('matched', [])
if matched:
    print('Keys in matched result:', list(matched[0].keys()))
    print('\nTop 10 Details:')
    for i, c in enumerate(matched[:10]):
        name = c.get('name_kr', '?')
        final = c.get('final_score', 0)
        v = c.get('v_norm', 0)
        g = c.get('g_norm', 0)
        b = c.get('b_norm', 0)
        d = c.get('depth', 0)
        print(f'{i+1:2d}. {name:10s} final:{final:.4f} v:{v:.4f} g:{g:.4f} b:{b:.4f} d:{d:.4f}')
else:
    print("No results found.")
