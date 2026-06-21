import sys
sys.stdout.reconfigure(encoding='utf-8')
from jd_compiler import api_search_v9

tests = [
    ('SoC NoC Network_on_Chip Chiplet semiconductor architect', 'SENIOR', '1aaad2d3-348d-48f7-8501-38d7c1f7df03', '한경환'),
    ('IPO preparation investor relations finance CFO fundraising', 'SENIOR', '1c3e3279-b0c5-4661-9dcf-7fa929dd47bb', '김진호'),
    ('GPU virtualization AI datacenter HPC network infra', 'MIDDLE', 'fbc27466-7587-45e6-b459-c2920b5d71fe', '김태경'),
    ('CISO information security game company', 'SENIOR', '32e22567-1b6f-8181-9992-d986271e941f', '오수영'),
]

for query, seniority, target_id, name in tests:
    r = api_search_v9(query, seniority=seniority)
    matched = r.get('matched', [])
    rank = next((i+1 for i,c in enumerate(matched) if c.get('id')==target_id), None)
    top3 = [(c.get('name_kr','?'), c.get('id','')[:8]) for c in matched[:3]]
    print(f'[{name}] rank={rank}')
    print(f'  Top3: {top3}')
