import sys
import json
import sqlite3
from jd_compiler import api_search_v9

sys.stdout.reconfigure(encoding='utf-8')

tests = [
    ('SoC NoC Network_on_Chip Chiplet semiconductor architect', 'All', '한경환', '1aaad2d3-348d-48f7-8501-38d7c1f7df03'),
    ('RISC-V NPU processor microarchitecture 6G baseband', 'All', '배정현', 'fafa2636-cf0b-42c1-8c18-598d089e9c61'),
    ('HPC CUDA parallel computing C++ Rust GPU', 'All', '박천혁', '3d322d13-0699-4453-b70e-5a4c2aac38f9'),
]

for query, seniority, name, target_id in tests:
    # We query with seniority='All' to avoid filtering out due to JUNIOR/MIDDLE mismatch
    r = api_search_v9(query, seniority=seniority)
    matched = r.get('matched', [])
    
    print(f'\n=== 쿼리: {query[:40]} ===')
    # Print top 5
    for i, c in enumerate(matched[:5]):
        print(f"  Rank {i+1}. {c.get('name_kr')} | score={c.get('final_score')[:5] if isinstance(c.get('final_score'), str) else float(c.get('final_score',0)):.4f} (g={c.get('g_score',0):.3f} v={c.get('v_score',0):.3f})")
        
    # Find our target rank
    found = False
    for idx, c in enumerate(matched):
        if c.get('id') == target_id:
            print(f'  -> [정답자 {name}] Found at rank {idx+1}: score={float(c.get("final_score",0)):.4f} (g={c.get("g_score",0):.3f} v={c.get("v_score",0):.3f})')
            found = True
            break
    if not found:
        print(f'  -> [정답자 {name}] NOT found in matched list of {len(matched)} candidates')
