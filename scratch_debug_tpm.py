import sys
import os

sys.stdout.reconfigure(encoding='utf-8')
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT_DIR)

from jd_compiler import api_search_v9

print("=== [Technical Program Manager] Search Analysis ===")
res = api_search_v9('Technical Program Manager')
matched = res.get('matched', [])
print(f"Total Matches: {len(matched)}")

found = False
for rank, cand in enumerate(matched):
    cname = cand.get('name_kr', '')
    cid = cand.get('id', '')
    ccompany = cand.get('current_company', '')
    csector = cand.get('sector', '')
    if cname in ('안유리', '권성환'):
        print(f"Rank {rank+1}: {cname} ({ccompany} | {csector}) - {cid[:8]}")
        found = True

if not found:
    print("Neither 안유리 nor 권성환 found in top results.")
