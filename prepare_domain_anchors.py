import json
import os
from openai import OpenAI
import numpy as np

# Secrets loading
SECRETS_PATH = "secrets.json"
with open(SECRETS_PATH, "r", encoding="utf-8") as f:
    secrets = json.load(f)

client = OpenAI(api_key=secrets.get("OPENAI_API_KEY"))

def get_embedding(text):
    res = client.embeddings.create(input=[text], model="text-embedding-3-small")
    return res.data[0].embedding

def prepare_domain_anchors():
    print("Preparing Domain Anchors (Golden Set Query Embeddings)...")
    
    with open('golden_dataset_v6.json', 'r', encoding='utf-8') as f:
        golden_set = json.load(f)
        
    anchors = []
    for i, item in enumerate(golden_set):
        query = item["query"]
        print(f"[{i+1}/{len(golden_set)}] Embedding query: {query[:30]}...")
        emb = get_embedding(query)
        
        anchors.append({
            "query": query,
            "relevant_ids": item.get("relevant_ids", []),
            "embedding": emb,
            # 스킬 정보가 있다면 미리 추출해서 넣어두면 더 빠름
            "target_nodes": item.get("target_nodes", []) 
        })
        
    with open('domain_anchors.json', 'w', encoding='utf-8') as f:
        json.dump(anchors, f, ensure_ascii=False, indent=2)
        
    print(f"Successfully saved {len(anchors)} anchors to domain_anchors.json")

if __name__ == "__main__":
    prepare_domain_anchors()
