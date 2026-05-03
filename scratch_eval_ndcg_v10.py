import json
import math
import sys
import os

# Ensure UTF-8 output for PowerShell
sys.stdout.reconfigure(encoding='utf-8')

# Root directory check
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT_DIR)

from jd_compiler import api_search_v10

def calculate_ndcg():
    dataset_path = 'golden_dataset_v6.json'
    if not os.path.exists(dataset_path):
        print(f"Error: {dataset_path} not found.")
        return

    with open(dataset_path, 'r', encoding='utf-8') as f:
        d = json.load(f)

    query_targets = {}
    for item in d:
        q = item.get('query') or item.get('jd_query')
        if not q: continue
        
        rel = item.get('relevant_ids') or []
        if not rel and item.get('candidate_neo4j_id'):
            rel = [item.get('candidate_neo4j_id')]
            
        if q not in query_targets:
            query_targets[q] = {
                'relevant': set(),
                'seniority': item.get('seniority', 'All')
            }
        for rid in rel:
            query_targets[q]['relevant'].add(str(rid).lower())

    scores = []
    print(f"=== [v10 Engine] NDCG Evaluation Start (Dataset: {dataset_path}) ===")
    print(f"Total Queries: {len(query_targets)}")
    print("-" * 50)

    for q, info in query_targets.items():
        relevant_ids = info['relevant']
        if not relevant_ids:
            continue
            
        # Search using v10
        res = api_search_v10(q, seniority=info['seniority'])
        matched = res.get('matched', [])
        
        # Calculate DCG@10
        dcg = 0.0
        hits = 0
        for i, cand in enumerate(matched[:10]):
            cid = str(cand.get('id', '')).lower()
            is_hit = False
            for rid in relevant_ids:
                if rid in cid or cid in rid:
                    is_hit = True
                    break
            
            if is_hit:
                dcg += 1.0 / math.log2(i + 2)
                hits += 1
        
        # Calculate IDCG@10
        idcg = sum(1.0 / math.log2(i + 2) for i in range(min(len(relevant_ids), 10)))
        
        score = dcg / idcg if idcg > 0 else 0.0
        scores.append(score)
        
        # Extract Explanation sample from top hit or top result
        expl = ""
        if matched:
            top_e = matched[0].get('explanation', {})
            expl = f" [Cov: {top_e.get('coverage_pct')}%]"
        
        print(f'{score:.2f} | hits:{hits}/{len(relevant_ids)} | {q[:40]}{expl}')

    if not scores:
        print("No scores calculated.")
        return

    avg_ndcg = sum(scores) / len(scores)
    perfect = sum(1 for s in scores if s >= 0.99)
    zero = sum(1 for s in scores if s < 0.01)

    print("-" * 50)
    print(f"FINAL AVERAGE NDCG@10 (v10): {avg_ndcg:.4f}")
    print(f"Perfect Scores: {perfect} / {len(scores)}")
    print(f"Zero Scores: {zero} / {len(scores)}")
    print("=" * 50)

if __name__ == "__main__":
    calculate_ndcg()
