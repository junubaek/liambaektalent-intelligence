
import asyncio
import json
import os
import numpy as np
from jd_compiler import search_vector_candidates_internal, search_graph_candidates_v10, CANONICAL_MAP, parse_jd_to_json

async def diagnose_v6():
    # 1. 대상 쿼리 (v6.json 1번 샘플)
    query = "Neural Network Operations Parallel Programming C++"
    relevant_ids = [
        "31f22567-1b6f-8106-a331-e438f877d966",
        "31f22567-1b6f-814d-9e7b-cf300cd3447f",
        "32e22567-1b6f-8194-85ac-c2d6a1fc37ba"
    ]
    
    print(f"--- Diagnostic Report for Query: {query} ---")
    
    # 2. Pure Vector Rank Check
    v_results = await search_vector_candidates_internal(query, top_k=500)
    v_ranks = {str(r["id"]): i+1 for i, r in enumerate(v_results)}
    
    print("\n[Tower 1: Vector Ranks]")
    for rid in relevant_ids:
        rank = v_ranks.get(rid, "Not in Top 500")
        score = next((r["score"] for r in v_results if str(r["id"]) == rid), 0.0)
        print(f"Candidate {rid}: Rank {rank} (Score: {score:.4f})")
        
    # 3. Pure Keyword/Expertise Rank Check
    extracted = parse_jd_to_json(query)
    target_skills = [CANONICAL_MAP.get(c.get("skill"), c.get("skill")) for c in extracted.get("conditions", []) if c.get("skill")]
    print(f"\nExtracted Skills: {target_skills}")
    
    pure_weights = {s: 1.0 for s in target_skills}
    g_results = await search_graph_candidates_v10(pure_weights, top_k=500)
    g_ranks = {str(r["id"]): i+1 for i, r in enumerate(g_results)}
    
    print("\n[Tower 2: Graph Ranks (Pure Keyword)]")
    for rid in relevant_ids:
        rank = g_ranks.get(rid, "Not in Top 500")
        score = next((r["weighted_score"] for r in g_results if str(r["id"]) == rid), 0.0)
        print(f"Candidate {rid}: Rank {rank} (Score: {score:.4f})")

if __name__ == "__main__":
    asyncio.run(diagnose_v6())
