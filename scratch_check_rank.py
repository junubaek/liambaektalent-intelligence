import json, sys, os
# Ensure ROOT_DIR is in path for jd_compiler
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT_DIR)

from jd_compiler import api_search_v9
sys.stdout.reconfigure(encoding='utf-8')

r = api_search_v9('LINUX AWS Architecture')
matched = r.get('matched', [])

targets = ['윤영필', '김효민']
print('Top 15:')
for i, c in enumerate(matched[:15]):
    name = c.get('name_kr','')
    marker = ' ← 정답' if name in targets else ''
    print(f'{i+1}. {name} | {round(c.get("final_score",0),3)}{marker}')
