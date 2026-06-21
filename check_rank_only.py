import sys
sys.path.append(r'C:\Users\cazam\Downloads\이력서자동분석검색시스템')
sys.stdout.reconfigure(encoding='utf-8')
from jd_compiler import api_search_v9

r = api_search_v9('CUDA GPU kernel C++ Rust high performance computing', seniority='MIDDLE')
matched = r.get('matched', [])
rank = next((i+1 for i,c in enumerate(matched) if c.get('id')=='3d322d13-0699-4453-b70e-5a4c2aac38f9'), None)
top3 = [(c.get('name_kr','?')[:6], c.get('id','')[:8]) for c in matched[:3]]
print(f'박천혁 rank={rank} | top3={top3}')
