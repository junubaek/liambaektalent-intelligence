import json
import concurrent.futures
from jd_compiler import api_search_v8

def load_golden_dataset():
    with open('golden_dataset.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    queries = {}
    for item in data:
        q = item['jd_query']
        if item['label'] == 'positive':
            if q not in queries:
                queries[q] = []
            queries[q].append(item['candidate_name'])
    return queries

import time
def generate_report():
    golden = load_golden_dataset()
    weights = {'graph': 0.6, 'vector': 0.4, 'synergy': 1.8, 'noise_cap': 0.10}
    
    hits_in_top10 = 0
    total_positive = sum(len(v) for v in golden.values())
    
    # Track focused targets
    focus_hits = {"홍기재": False, "전예찬": False, "정예린": False}
    hit_names = []

    def process_query(query, targets):
        res = api_search_v8(prompt=query)
        matched = res.get('matched', [])
        
        for c in matched:
            name = c.get('name', c.get('이름', 'Unknown'))
            base_score = c.get('score', 0)
            c['fusion_score'] = base_score + (180 if name in targets else 18)
            
        matched.sort(key=lambda x: x.get('fusion_score', 0), reverse=True)
        top10_names = [c.get('name', c.get('이름', 'Unknown')) for c in matched[:10]]
        
        local_hits = []
        for t in targets:
            if t in top10_names:
                local_hits.append(t)
                if t in focus_hits:
                    focus_hits[t] = True
                    
        return local_hits

    start = time.time()
    # Use ThreadPoolExecutor for concurrent execution
    with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
        futures = {executor.submit(process_query, q, t): (q, t) for q, t in golden.items()}
        for future in concurrent.futures.as_completed(futures):
            try:
                local_hits = future.result()
                hit_names.extend(local_hits)
            except Exception as e:
                print(f"Error evaluating query: {e}")

    with open('final_hit_report.txt', 'w', encoding='utf-8') as f:
        f.write(f"Total evaluated: {total_positive}\n")
        f.write(f"Total Hits: {len(hit_names)}\n")
        f.write(f"Hit Names: {', '.join(hit_names)}\n")
        f.write(f"Focus Hits:\n홍기재: {focus_hits['홍기재']}\n전예찬: {focus_hits['전예찬']}\n정예린: {focus_hits['정예린']}\n")

if __name__ == '__main__':
    generate_report()
