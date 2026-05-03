import asyncio
import json
from jd_compiler import api_search_v10_14
import sqlite3
import os

async def deep_diagnose():
    query = "Spring Fintech MSSQL"
    target_id = "33522567-1b6f-817e-a77b-ffc7e1b8d5d4"
    
    print(f"Deep Diagnosis for ID: {target_id} on Query: {query}")
    
    # 1. Check in Database
    conn = sqlite3.connect('candidates.db')
    row = conn.execute("SELECT name_kr, raw_text FROM candidates WHERE id = ?", (target_id,)).fetchone()
    if row:
        print(f"Found in DB: {row[0]}")
        text = row[1].lower()
        print(f"Has 'spring': {'spring' in text}")
        print(f"Has 'mssql': {'mssql' in text}")
        print(f"Has 'fintech': {'fintech' in text}")
    else:
        print("ERROR: Target ID NOT in candidates.db")
    conn.close()

    # 2. Run Search and see where it is
    results = await api_search_v10_14({"query": query, "top_k": 500})
    
    rank = -1
    for i, res in enumerate(results):
        if str(res["id"]) == target_id:
            rank = i + 1
            print(f"Candidate found at Rank {rank} with Score {res['score']}")
            print(f"Layers: {res.get('layers', 'N/A')}")
            break
            
    if rank == -1:
        print("CRITICAL: Candidate NOT found in Top 500 recall!")

if __name__ == "__main__":
    asyncio.run(deep_diagnose())
