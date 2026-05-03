import asyncio
import json
import math
import os
from jd_compiler import api_search_v10_17

async def diagnose_query(query_idx=15):
    with open('golden_dataset_v6.json', 'r', encoding='utf-8') as f:
        golden = json.load(f)
    
    item = golden[query_idx]
    query = item["query"]
    print(f"Diagnosing Query #{query_idx}: {query}")
    
    relevant_ids = set()
    if isinstance(item.get("relevant_ids"), list):
        flat_relevant = []
        for rid in item["relevant_ids"]:
            if isinstance(rid, list): flat_relevant.extend(rid)
            else: flat_relevant.append(rid)
        relevant_ids = set([str(r) for r in flat_relevant])

    results = await api_search_v10_17({"query": query, "top_k": 20})
    
    print("\nTop 20 Results:")
    for i, res in enumerate(results):
        cid = str(res["id"])
        is_rel = " [RELEVANT]" if cid in relevant_ids else ""
        print(f"{i+1}. {res['name']} ({cid}) - Score: {res['score']}{is_rel}")
        if cid in relevant_ids:
            # Check raw components
            print(f"   - V_raw: {res.get('v_raw')}, G_raw: {res.get('g_raw')}, B_raw: {res.get('b_raw')}, D_raw: {res.get('d_raw')}")
    
    # Check Recall Pool
    from jd_compiler import search_vector_candidates_internal, get_bm25_top_v9
    v_results = await search_vector_candidates_internal(query, top_k=200)
    v_ids = set(res["id"] for res in v_results)
    bm_map = get_bm25_top_v9(query, top_k=100)
    bm_ids = set(bm_map.keys())
    
    print(f"\nChecking Recall for Targets: {relevant_ids}")
    print(f"Target in Vector Recall: {relevant_ids & v_ids}")
    print(f"Target in BM25 Recall: {relevant_ids & bm_ids}")

if __name__ == "__main__":
    asyncio.run(diagnose_query(21))
