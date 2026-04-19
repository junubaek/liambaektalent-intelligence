import sys
import os
import re
import json
import numpy as np

sys.stdout.reconfigure(encoding='utf-8')
ROOT_DIR = r"c:\Users\cazam\Downloads\이력서자동분석검색시스템"
jd_path = os.path.join(ROOT_DIR, "jd_compiler.py")

with open(jd_path, "r", encoding="utf-8") as f:
    original_content = f.read()

combinations = [
    (1, 0.2, 0.8),
    (2, 0.4, 0.6),
    (3, 0.5, 0.5),
    (4, 0.6, 0.4),
    (5, 0.8, 0.2)
]

def replace_weights(wv, wg):
    # Match lines like: final_score = (graph_score * 0.85) + (v_score * 0.15)
    text = re.sub(
        r"final_score\s*=\s*\(graph_score\s*\*\s*[\d\.]+\)\s*\+\s*\(v_score\s*\*\s*[\d\.]+\)",
        f"final_score = (graph_score * {wg}) + (v_score * {wv})",
        original_content
    )
    with open(jd_path, "w", encoding="utf-8") as f:
        f.write(text)

def dcg(relevances, k=10):
    relevances = np.asarray(relevances, dtype=float)[:k]
    if relevances.size:
        return np.sum((2**relevances - 1) / np.log2(np.arange(2, relevances.size + 2)))
    return 0.

def ndcg(relevances, k=10):
    best_dcg = dcg(sorted(relevances, reverse=True), k)
    if best_dcg == 0:
        return 0.
    return dcg(relevances, k) / best_dcg

results = []

try:
    with open(os.path.join(ROOT_DIR, 'golden_dataset_v3.json'), 'r', encoding='utf-8') as f:
        ds = json.load(f)
        
    queries_dict = {}
    for item in ds:
        q = item.get('jd_query')
        cname = item.get('candidate_name')
        if not q or not cname: continue
        clean_name = cname.split('(')[0].replace(' ', '').strip()
        if q not in queries_dict:
            queries_dict[q] = set()
        queries_dict[q].add(clean_name)
        
    for idx, wv, wg in combinations:
        print(f"Testing Combo {idx}: Wv={wv}, Wg={wg} ...")
        replace_weights(wv, wg)
        
        # dynamic import per cycle to test changes
        import importlib
        import jd_compiler
        importlib.reload(jd_compiler)
        
        ndcg_list = []
        for q, pos_names in queries_dict.items():
            res = jd_compiler.api_search_v8(q)
            matched = res.get('matched', [])[:10]
            relevances = []
            for m in matched:
                raw_cname = m.get('name_kr', '')
                clean_cname = raw_cname.split('(')[0].replace(' ', '').strip()
                relevances.append(1 if clean_cname in pos_names else 0)
            
            val = 0.0 if sum(relevances) == 0 else ndcg(relevances)
            ndcg_list.append((q, val))
            
        avg_ndcg = sum(v for _, v in ndcg_list) / len(ndcg_list)
        ones = len([x for x in ndcg_list if x[1] >= 0.99])
        mids = len([x for x in ndcg_list if 0 < x[1] < 0.99])
        zeroes = len([x for x in ndcg_list if x[1] == 0])

        out = f"{idx}    | {wv} | {wg} | {avg_ndcg:.4f} |  {ones}  |  {mids}  |  {zeroes}"
        results.append(out)
        print(out)
except Exception as e:
    print(f"Error testing: {e}")
finally:
    with open(jd_path, "w", encoding="utf-8") as f:
        f.write(original_content)

print("\n--- Final Table ---")
print("조합 | Wv  | Wg  | NDCG   | 완벽 | 부분 | 실패")
for r in results:
    print(r)
