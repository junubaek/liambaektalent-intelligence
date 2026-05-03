import asyncio
import json
import math
from jd_compiler import api_search_v10_14

def calculate_ndcg_single(relevant_ids, results, k=10):
    if not relevant_ids: return 0.0
    dcg = 0.0
    for i, res in enumerate(results[:k]):
        if str(res.get("id")) in relevant_ids:
            dcg += 1.0 / math.log2(i + 2)
    idcg = 0.0
    num_relevant = min(len(relevant_ids), k)
    for i in range(num_relevant):
        idcg += 1.0 / math.log2(i + 2)
    return dcg / idcg if idcg > 0 else 0.0

async def full_audit():
    with open('golden_dataset_v6.json', 'r', encoding='utf-8') as f:
        golden_set = json.load(f)
    
    results_summary = []
    for idx, item in enumerate(golden_set):
        query = item["query"]
        relevant_ids = set()
        if isinstance(item.get("relevant_ids"), list):
            for rid in item["relevant_ids"]:
                if isinstance(rid, list): relevant_ids.update([str(r) for r in rid])
                else: relevant_ids.add(str(rid))
        
        try:
            results = await api_search_v10_14({"query": query, "top_k": 10})
            ndcg = calculate_ndcg_single(relevant_ids, results, k=10)
            results_summary.append((idx, ndcg, query))
            print(f"[{idx}] NDCG: {ndcg:.4f} | {query}")
        except Exception as e:
            print(f"[{idx}] ERROR: {e}")
            
    print("\n" + "="*50)
    print("CRITICAL FAILURES (NDCG < 0.2):")
    for idx, ndcg, query in results_summary:
        if ndcg < 0.2:
            print(f"FAILED [{idx}] ({ndcg:.4f}): {query}")
    print("="*50)

if __name__ == "__main__":
    asyncio.run(full_audit())
