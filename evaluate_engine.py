import json
import math
from jd_compiler import api_search_v8

def load_golden_dataset():
    with open('golden_dataset.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    queries = {}
    for item in data:
        q = item['jd_query']
        if item['label'] == 'positive':
            if q not in queries:
                queries[q] = set()
            queries[q].add(item['candidate_name'])
    return queries

def run_evaluation_pipeline(weights=None):
    if weights is None:
        weights = {"graph": 0.7, "vector": 0.3, "synergy": 1.5, "noise_cap": 0.10}
        
    global_jd_compiler_weights = weights # Simulate setting weights, ideally pass to JD Compiler
    # For now, we will just use the returned API results since the jd_compiler itself doesn't easily expose this parameter at the top level
    
    golden = load_golden_dataset()
    ndcg_sum = 0
    total_queries = 0
    k = 10
    
    for query, positive_targets in list(golden.items())[:15]: # Limiting to 15 queries for speed
        res = api_search_v8(prompt=query)
        matched = res.get('matched', [])
        
        # Calculate DCG@10
        dcg = 0
        for i, c in enumerate(matched[:k]):
            if c.get('name') in positive_targets or c.get('name_kr') in positive_targets:
                rel = 1
                dcg += rel / math.log2(i + 1 + 1)
                
        # Calculate IDCG@10
        idcg = 0
        for i in range(min(k, len(positive_targets))):
            idcg += 1 / math.log2(i + 1 + 1)
            
        ndcg = dcg / idcg if idcg > 0 else 0
        ndcg_sum += ndcg
        total_queries += 1
        
    return ndcg_sum / total_queries if total_queries > 0 else 0
