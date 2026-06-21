import sys
sys.stdout.reconfigure(encoding='utf-8')
from jd_compiler import api_search_v9

tests = [
    ('GPU virtualization AI datacenter HPC network infra', 'MIDDLE', 'fbc27466-7587-45e6-b459-c2920b5d71fe', '김태경'),
    ('SCM logistics operations cost management', 'MIDDLE', '31f22567-1b6f-8152-93ca-ca5ab3080016', '유정한'),
    ('CISO information security game company', 'SENIOR', '32e22567-1b6f-8181-9992-d986271e941f', '오수영'),
    ('VC venture capital deal sourcing portfolio startup', 'SENIOR', '4b4c3372-401b-4897-a9b3-d36a3ba3de37', '김형수'),
    ('on-device AI inference embedded AI semiconductor', 'SENIOR', 'ba4abc09-302e-4fd4-ae93-b8af52aed567', '하현재'),
    ('healthcare AI computer vision deep learning medical imaging', 'MIDDLE', '32022567-1b6f-819f-b62e-fa5ecb02e3de', '김진영'),
    ('IPO IR strategic planning fundraising finance', 'SENIOR', '1c3e3279-b0c5-4661-9dcf-7fa929dd47bb', '김진호'),
    ('HPC CUDA parallel computing C++ Rust GPU', 'MIDDLE', '3d322d13-0699-4453-b70e-5a4c2aac38f9', '박천혁'),
]

for query, seniority, target_id, name in tests:
    r = api_search_v9(query, seniority=seniority)
    matched = r.get('matched', [])
    rank = next((i+1 for i,c in enumerate(matched) if c.get('id')==target_id), None)
    top1 = matched[0] if matched else {}
    print(f"[{name}] rank={rank} | 1위={top1.get('name_kr','?')} (score={top1.get('final_score',0):.3f}, g={top1.get('g_score',0):.3f}, v={top1.get('v_score',0):.3f})")
