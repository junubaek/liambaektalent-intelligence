import sys
import os
import subprocess
import re

sys.stdout.reconfigure(encoding='utf-8')
ROOT_DIR = r"c:\Users\cazam\Downloads\이력서자동분석검색시스템"
jd_path = os.path.join(ROOT_DIR, "jd_compiler.py")

with open(jd_path, "r", encoding="utf-8") as f:
    original_content = f.read()

combinations = [
    # Synergy, Depth Multipliers mapped to values
    ("A", 1.4, 1.3, "{1: 1.0, 2: 1.1, 3: 1.2, 4: 1.3}"),
    ("B", 1.6, 1.4, "{1: 1.0, 2: 1.2, 3: 1.3, 4: 1.4}"),
    ("C", 1.8, 1.6, "{1: 1.0, 2: 1.3, 3: 1.5, 4: 1.6}"),
    ("D", 2.0, 1.8, "{1: 1.0, 2: 1.4, 3: 1.6, 4: 1.8}")
]

def replace_multipliers(syn_val, depth_str):
    # depth replace
    c = re.sub(
        r"DEPTH_MULTIPLIER\s*=\s*\{[^\}]+\}",
        f"DEPTH_MULTIPLIER = {depth_str}", 
        original_content
    )
    # synergy parameter mock? Actually synergy 1.8 is typically simulated for "조합 C" 
    # Let's dynamically inject a multiplier in inject_node_affinity.
    c = c.replace(
        '"weight": weight,',
        f'"weight": weight * ({syn_val} / 1.8),'
    )
    with open(jd_path, "w", encoding="utf-8") as f:
        f.write(c)

results = []

for name, syn, dep, d_str in combinations:
    print(f"Testing Option {name}: Synergy={syn}, Depth={dep} ...")
    replace_multipliers(syn, d_str)
    
    # We will compute NDCG using the api natively
    import json
    import numpy as np

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

    try:
        from jd_compiler import api_search_v8
        import importlib
        import jd_compiler
        importlib.reload(jd_compiler)
        
        with open('golden_dataset_v3.json', 'r', encoding='utf-8') as f:
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

        results.append(f"{name} | {syn} | {dep} | {avg_ndcg:.4f} | {ones} | {mids} | {zeroes}")
        print(results[-1])
    except Exception as e:
        print(f"Error testing {name}: {e}")
        import traceback
        traceback.print_exc()

with open("opt2_results.txt", "w", encoding="utf-8") as rf:
    rf.write("\n".join(results))

with open(jd_path, "w", encoding="utf-8") as f:
    f.write(original_content)
