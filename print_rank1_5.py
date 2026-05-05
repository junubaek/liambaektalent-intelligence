import sys
from jd_compiler import api_search_v9

sys.stdout.reconfigure(encoding='utf-8')

res = api_search_v9("senior cfo")
matched = res.get('matched', [])

for i, c in enumerate(matched[:5]):
    print(f"Rank {i+1}: {c.get('name_kr')} | Score: {c.get('final_score')}")
