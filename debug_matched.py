import sys
sys.path.append(r'C:\Users\cazam\Downloads\이력서자동분석검색시스템')
from jd_compiler import api_search_v9

r = api_search_v9('GPU virtualization AI datacenter HPC network infra', seniority='MIDDLE')
matched = r.get('matched', [])
print("Matched count:", len(matched))
for idx, c in enumerate(matched[:15]):
    print(f"Rank {idx+1}: {c.get('name_kr')} | ID: {c.get('id')} | Company: {c.get('current_company')}")
