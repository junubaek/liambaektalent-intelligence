import sys
import os

# Ensure UTF-8 output
sys.stdout.reconfigure(encoding='utf-8')
sys.path.append(r'C:\Users\cazam\Downloads\이력서자동분석검색시스템')

from jd_compiler import api_search_v9

query = "NPU 드라이버 커널 엔지니어 찾아줘"
print(f"Executing search for query: '{query}'...")

try:
    res = api_search_v9(query)
    matched = res.get('matched', [])
    
    print("\n--- Top 10 Search Results (After Edge Normalization Fix) ---")
    print("-" * 70)
    jeon_found = False
    for i, c in enumerate(matched[:15]):
        name = c.get('name_kr') or c.get('name')
        score = c.get('final_score') or 0.0
        g_score = c.get('g_score') or 0.0
        v_score = c.get('v_score') or 0.0
        bm_score = c.get('bm_score') or 0.0
        depth_score = c.get('depth_score') or 0.0
        sector = c.get('sector') or ''
        company = c.get('current_company') or '미상'
        
        print(f"{i+1:2d}. {name} | Score: {score:.4f} [G: {g_score:.4f}, V: {v_score:.4f}, B: {bm_score:.4f}, D: {depth_score:.4f}] | {company} ({sector})")
        if '전형준' in name or 'Jeon' in name:
            jeon_found = True
            
    if not jeon_found:
        print("\n* 전형준 not found in Top 15. Searching full list...")
        for i, c in enumerate(matched):
            name = c.get('name_kr') or c.get('name')
            if '전형준' in name or 'Jeon' in name:
                score = c.get('final_score') or 0.0
                g_score = c.get('g_score') or 0.0
                v_score = c.get('v_score') or 0.0
                bm_score = c.get('bm_score') or 0.0
                depth_score = c.get('depth_score') or 0.0
                sector = c.get('sector') or ''
                company = c.get('current_company') or '미상'
                print(f"-> {i+1}th place: {name} | Score: {score:.4f} [G: {g_score:.4f}, V: {v_score:.4f}, B: {bm_score:.4f}, D: {depth_score:.4f}] | {company} ({sector})")
                jeon_found = True
                break
                
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
