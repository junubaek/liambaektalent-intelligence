import asyncio
import json
import math
import os
from jd_compiler import api_search_v10_20

def calculate_ndcg(relevant_ids, results, k=10):
    if not relevant_ids: return 0.0
    
    # 1. DCG 계산
    dcg = 0.0
    for i, res in enumerate(results[:k]):
        cid = str(res.get("id"))
        if cid in relevant_ids:
            dcg += 1.0 / math.log2(i + 2)
            
    # 2. IDCG 계산 (이상적인 경우)
    idcg = 0.0
    num_relevant = min(len(relevant_ids), k)
    for i in range(num_relevant):
        idcg += 1.0 / math.log2(i + 2)
        
    if idcg == 0: return 0.0
    return dcg / idcg

async def benchmark_v10_20():
    with open('golden_dataset_v6.json', 'r', encoding='utf-8') as f:
        golden_set = json.load(f)
    
    print(f"Starting NDCG@10 Benchmark for v10.20 GRAVITY MASTER PATCHED (Total: {len(golden_set)} queries)")
    
    total_ndcg = 0.0
    count = 0
    
    for item in golden_set:
        query = item["query"]
        relevant_ids = set()
        if isinstance(item.get("relevant_ids"), list):
            flat_relevant = []
            for rid in item["relevant_ids"]:
                if isinstance(rid, list): flat_relevant.extend(rid)
                else: flat_relevant.append(rid)
            relevant_ids = set([str(r) for r in flat_relevant])

        try:
            results = await api_search_v10_20({"query": query, "top_k": 10})
            ndcg = calculate_ndcg(relevant_ids, results, k=10)
            
            total_ndcg += ndcg
            count += 1
            
            if count % 5 == 0:
                print(f"Progress: {count}/{len(golden_set)} | Current Avg NDCG: {total_ndcg/count:.4f}")
        except Exception as e:
            print(f"Error on query '{query}': {e}")
            
    final_avg = total_ndcg / count if count > 0 else 0
    print("\n" + "="*40)
    print(f"FINAL v10.20 GRAVITY MASTER PATCHED NDCG@10: {final_avg:.4f}")
    print("="*40)

if __name__ == "__main__":
    asyncio.run(benchmark_v10_20())
