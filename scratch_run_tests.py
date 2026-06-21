import sys
import json
sys.stdout.reconfigure(encoding='utf-8')
from jd_compiler import api_search_v9

tests = [
    ('SoC NoC Network_on_Chip Chiplet semiconductor architect', 'SENIOR', '한경환', '1aaad2d3-348d-48f7-8501-38d7c1f7df03'),
    ('RISC-V NPU processor microarchitecture 6G baseband', 'MIDDLE', '배정현', 'fafa2636-cf0b-42c1-8c18-598d089e9c61'),
    ('HPC CUDA parallel computing C++ Rust GPU', 'MIDDLE', '박천혁', '3d322d13-0699-4453-b70e-5a4c2aac38f9'),
]

for query, seniority, name, target_id in tests:
    r = api_search_v9(query, seniority=seniority)
    matched = r.get('matched', [])
    print(f'\n쿼리: {query[:40]}')
    for i, c in enumerate(matched[:10]):
        hit = ' ← 정답' if c.get('id') == target_id else ''
        print(f'  {i+1}. {c.get("name_kr","?")[:8]} | score={c.get("final_score",0):.3f} (g={c.get("g_score",0):.3f} v={c.get("v_score",0):.3f}){hit}')
