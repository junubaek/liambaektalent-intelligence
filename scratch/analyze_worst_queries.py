import sys
import json
import os
import math

# Ensure UTF-8 output
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

# Set PYTHONPATH
sys.path.insert(0, os.getcwd())
from jd_compiler import api_search_v9

with open('golden_dataset_v8.json', 'r', encoding='utf-8') as f:
    golden = json.load(f)

def calculate_ndcg(found_ranks, total_relevant):
    if not found_ranks: return 0.0
    dcg = sum(1.0 / math.log2(rank + 1) for rank in found_ranks)
    idcg = sum(1.0 / math.log2(i + 2) for i in range(total_relevant))
    return dcg / idcg

results = []
for q in golden:
    query = q.get('query', '')
    rel_ids = q.get('relevant_ids', [])
    rel_names = q.get('relevant_names', [])
    
    res = api_search_v9(prompt=query, seniority='All')
    candidates = res.get('matched', [])
    
    found_ranks = []
    found_details = []
    for i, c in enumerate(candidates):
        if c.get('id') in rel_ids:
            found_ranks.append(i + 1)
            found_details.append(c)
    
    # Calculate simple NDCG@10 for sorting
    ndcg = calculate_ndcg([r for r in found_ranks if r <= 10], len(rel_ids))
    results.append({
        'ndcg': ndcg,
        'query': query,
        'rel_names': rel_names,
        'ranks': found_ranks[:5],
        'top_results': candidates[:3],
        'target_details': found_details[:1]
    })

# Sort by NDCG ascending
results.sort(key=lambda x: x['ndcg'])

print("=== NDCG LOWEST QUERIES TOP 5 ANALYSIS ===")
print("-" * 60)

for item in results[:5]:
    print(f"Query: '{item['query']}'")
    print(f"Target: {item['rel_names']} | Actual Ranks: {item['ranks']}")
    print(f"NDCG@10: {item['ndcg']:.4f}")
    
    print("\nTop 3 Rankers:")
    for i, c in enumerate(item['top_results']):
        print(f"  {i+1}. {c.get('name_kr'):10s} | FINAL:{c.get('final_score'):.3f} | V:{c.get('v_score'):.3f} | G:{c.get('g_score'):.3f} | D:{c.get('depth_score'):.3f}")
        
    if item['target_details']:
        t = item['target_details'][0]
        print(f"\nTarget Info ({t.get('name_kr')}):")
        print(f"  FINAL:{t.get('final_score'):.3f} | V:{t.get('v_score'):.3f} | G:{t.get('g_score'):.3f} | D:{t.get('depth_score'):.3f}")
        print(f"  Matched Skills: {t.get('matched_edges', [])[:10]}")
    else:
        print("\nTarget NOT FOUND in search results pool!")
        
    print("-" * 60)
