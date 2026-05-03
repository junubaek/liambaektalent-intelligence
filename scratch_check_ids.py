import json, sys, os
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT_DIR)
from jd_compiler import api_search_v9

sys.stdout.reconfigure(encoding='utf-8')

r = api_search_v9('LINUX AWS Architecture')
matched = r.get('matched', [])

# 골든셋 정답 ID
target_ids = [
    '31f22567-1b6f-8193-8cb9-d78eb4c59593',
    '33522567-1b6f-81a3-ac63-e62ab98e6793'
]

print('Top 10 IDs:')
for i, c in enumerate(matched[:10]):
    cid = str(c.get('id', ''))
    name = c.get('name_kr', '')
    hit = any(t.lower() in cid.lower() or cid.lower() in t.lower() for t in target_ids)
    print(f'{i+1}. {name} | {cid[:40]} | hit:{hit}')
