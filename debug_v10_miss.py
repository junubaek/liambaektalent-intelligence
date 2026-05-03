import json
import sys
import os

# Ensure UTF-8 output
sys.stdout.reconfigure(encoding='utf-8')

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT_DIR)

from jd_compiler import api_search_v10

def debug_misses():
    with open('golden_dataset_v7.json', 'r', encoding='utf-8') as f:
        d = json.load(f)

    for item in d:
        query = item['query']
        target_name = item['expected_name']
        target_ids = [tid.lower() for tid in item['relevant_ids']]
        
        print(f"\n=== Debugging: {target_name} ({query[:30]}...) ===")
        
        res = api_search_v10(query)
        matched = res.get('matched', [])
        
        # Check if target is in results
        found_in_top_50 = False
        target_rank = -1
        
        for i, cand in enumerate(matched):
            cid = str(cand.get('id', '')).lower()
            if any(tid == cid for tid in target_ids):
                found_in_top_50 = True
                target_rank = i + 1
                print(f"✅ FOUND in Top 50! Rank: {target_rank}")
                print(f"   - Score: {cand['score']} | ws_score: {cand['ws_score']}")
                print(f"   - Coverage: {cand.get('coverage_score')} | Vector: {cand.get('vector_score')}")
                print(f"   - Explanation: {cand.get('explanation')}")
                break
        
        if not found_in_top_50:
            print(f"❌ NOT FOUND in Top 50.")
            # Let's see who is at #1
            if matched:
                top1 = matched[0]
                print(f"   - Current #1: {top1['name_kr']} (Score: {top1['score']}, Cov: {top1.get('coverage_score')})")
            else:
                print("   - No results matched at all.")

if __name__ == "__main__":
    debug_misses()
