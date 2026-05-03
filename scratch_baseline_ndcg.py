import asyncio
import json
import math
import sqlite3
import re
import os

def calculate_ndcg(relevant_ids, results, k=10):
    if not relevant_ids: return 0.0
    dcg = 0.0
    for i, res in enumerate(results[:k]):
        if str(res.get("id")) in relevant_ids:
            dcg += 1.0 / math.log2(i + 2)
    idcg = 0.0
    for i in range(min(len(relevant_ids), k)):
        idcg += 1.0 / math.log2(i + 2)
    return dcg / idcg if idcg > 0 else 0.0

async def pure_keyword_search(query, top_k=20):
    words = re.findall(r'[a-zA-Z0-9가-힣]{2,}', query.upper())
    conn = sqlite3.connect('candidates.db')
    cursor = conn.cursor()
    
    # Simple counting of word matches in raw_text
    cursor.execute("SELECT id, name_kr, raw_text FROM candidates")
    rows = cursor.fetchall()
    
    scored = []
    for cid, name, text in rows:
        if not text: continue
        text = text.upper()
        matches = sum(1 for w in words if w in text)
        if matches > 0:
            scored.append({"id": cid, "name": name, "score": matches})
            
    scored.sort(key=lambda x: x["score"], reverse=True)
    conn.close()
    return scored[:top_k]

async def run_baseline():
    with open('golden_dataset_v6.json', 'r', encoding='utf-8') as f:
        golden = json.load(f)
    
    total = 0.0
    for item in golden:
        q = item["query"]
        rids = set()
        for r in item["relevant_ids"]:
            if isinstance(r, list): rids.update([str(x) for x in r])
            else: rids.add(str(r))
            
        results = await pure_keyword_search(q)
        total += calculate_ndcg(rids, results)
        
    print(f"PURE KEYWORD BASELINE NDCG@10: {total/len(golden):.4f}")

if __name__ == "__main__":
    asyncio.run(run_baseline())
