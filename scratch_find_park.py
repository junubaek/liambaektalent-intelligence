from jd_compiler import api_search_v9

r = api_search_v9('HPC CUDA parallel computing C++ Rust GPU', seniority='MIDDLE')
matched = r.get('matched', [])
print(f"Total matched: {len(matched)}")
for idx, c in enumerate(matched):
    if c.get('id') == '3d322d13-0699-4453-b70e-5a4c2aac38f9' or '박천혁' in c.get('name_kr', ''):
        print(f"Found at rank {idx+1}: name={c.get('name_kr')}, score={c.get('final_score')}, g={c.get('g_score')}, v={c.get('v_score')}")
        break
else:
    print("Not found")
