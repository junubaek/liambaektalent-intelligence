import json
import math
import sys
import os

# Ensure UTF-8 output for PowerShell
sys.stdout.reconfigure(encoding='utf-8')

# Root directory check
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT_DIR)

from jd_compiler import api_search_v9

def calculate_ndcg():
    dataset_path = 'golden_dataset_v8.json'
    if not os.path.exists(dataset_path):
        print(f"Error: {dataset_path} not found.")
        return

    with open(dataset_path, 'r', encoding='utf-8') as f:
        d = json.load(f)

    query_targets = {}
    for item in d:
        q = item.get('query') or item.get('jd_query')
        if not q: continue
        
        rel_ids = item.get('relevant_ids') or []
        rel_scores = item.get('relevance_scores') or {}
        
        if q not in query_targets:
            query_targets[q] = {
                'relevant_ids': set(),
                'relevance_scores': {}, # id -> score
                'relevant_names': set(),
                'seniority': item.get('seniority', 'All')
            }
        
        for rid in rel_ids:
            s_rid = str(rid).lower()
            query_targets[q]['relevant_ids'].add(s_rid)
            query_targets[q]['relevance_scores'][s_rid] = rel_scores.get(rid, 0.3)
            
        for rname in item.get('relevant_names', []):
            query_targets[q]['relevant_names'].add(rname.lower())

    scores = []
    print(f"=== NDCG Evaluation Start (Graded Relevance, Dataset: {dataset_path}) ===")
    print(f"Total Queries: {len(query_targets)}")
    print("-" * 50)

    for q, info in query_targets.items():
        relevant_ids = info['relevant_ids']
        relevance_scores = info['relevance_scores']
        relevant_names = info['relevant_names']
        
        if not relevant_ids: continue
            
        # Search using v9
        res = api_search_v9(q, seniority=info['seniority'])
        matched = res.get('matched', [])
        
        # Calculate DCG@10
        dcg = 0.0
        hits = 0
        for i, cand in enumerate(matched[:10]):
            cid = str(cand.get('id', '')).lower()
            cand_name = str(cand.get('name_kr', '')).lower()
            
            rel = 0.0
            # 1. ID matching
            if cid in relevance_scores:
                rel = relevance_scores[cid]
            
            # 2. Name matching backup
            if rel == 0.0 and cand_name in relevant_names:
                # Find the score for this name (heuristic: use max score among relevant IDs if name matches)
                # But we don't have name->score map easily. Let's assume 0.3 if only name matches.
                rel = 0.3 
            
            if rel > 0:
                dcg += rel / math.log2(i + 2)
                hits += 1

        # Calculate IDCG@10
        # Optimal ranking: all possible relevance scores sorted descending
        all_rels = sorted(relevance_scores.values(), reverse=True)
        idcg = sum(all_rels[i] / math.log2(i + 2) for i in range(min(len(all_rels), 10)))
        
        score = dcg / idcg if idcg > 0 else 0.0
        scores.append(score)
        
        print(f'{score:.4f} | hits:{hits}/{len(relevant_ids)} | {q[:45]}')
        for i, cand in enumerate(matched[:10]):
            cid = str(cand.get('id', '')).lower()
            cand_name = str(cand.get('name_kr', '')).lower()
            rel = relevance_scores.get(cid, 0.0)
            if rel == 0 and cand_name in relevant_names: rel = 0.3
            marker = f" [HIT:{rel}]" if rel > 0 else ""
            print(f'  {i+1}. {cand.get("name_kr", "Unknown")} ({cid[:8]}){marker}')
        print("-" * 30)

    if not scores:
        print("No scores calculated.")
        return

    avg_ndcg = sum(scores) / len(scores)
    print("-" * 50)
    print(f"FINAL AVERAGE NDCG@10: {avg_ndcg:.4f}")
    print("=" * 50)

if __name__ == "__main__":
    calculate_ndcg()
