
import asyncio
import json
import os
import numpy as np
from jd_compiler import search_vector_candidates_internal, search_graph_candidates_v10, CANONICAL_MAP, parse_jd_to_json

async def diagnose_query():
    # 1. 대상 쿼리 (골든셋 1번 샘플)
    query = "경영전략을 수립하고 자금 운용(Treasury) 및 외환 관리를 총괄하며, ERP 시스템을 구축해본 재무 전문가"
    relevant_ids = ["10", "11"] # 김대중 등 예상 정답
    
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
    # (Extract skills first)
    extracted = parse_jd_to_json(query)
    target_skills = [CANONICAL_MAP.get(c.get("skill"), c.get("skill")) for c in extracted.get("conditions", []) if c.get("skill")]
    print(f"\nExtracted Skills: {target_skills}")
    
    # Mock expert weights (All 1.0 for pure keyword check)
    pure_weights = {s: 1.0 for s in target_skills}
    g_results = await search_graph_candidates_v10(pure_weights, top_k=500)
    g_ranks = {str(r["id"]): i+1 for i, r in enumerate(g_results)}
    
    print("\n[Tower 2: Graph Ranks (Pure Keyword)]")
    for rid in relevant_ids:
        rank = g_ranks.get(rid, "Not in Top 500")
        score = next((r["weighted_score"] for r in g_results if str(r["id"]) == rid), 0.0)
        print(f"Candidate {rid}: Rank {rank} (Score: {score:.4f})")

if __name__ == "__main__":
    asyncio.run(diagnose_query())
