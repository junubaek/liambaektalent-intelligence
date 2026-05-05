import sys
from jd_compiler import api_search_v9

sys.stdout.reconfigure(encoding='utf-8')

res = api_search_v9("senior cfo")
matched = res.get('matched', [])

print(f"Top {len(matched)} names:")
for i, c in enumerate(matched):
    print(f"{i+1}: {c.get('name_kr')} ({c.get('id')}) - Score: {c.get('hybrid_score')}")
