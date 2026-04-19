import subprocess
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

combinations = [
    ("Base", 30, 30),
    ("A", 75, 30),
    ("B", 75, 50),
    ("C", 100, 50)
]

with open('jd_compiler.py', 'r', encoding='utf-8') as f:
    text = f.read()

results = {}

try:
    for name, top_v, top_g in combinations:
        print(f"Testing Combination {name} (V={top_v}, G={top_g})")
        
        with open('jd_compiler.py', 'r', encoding='utf-8') as f:
            current_text = f.read()
        
        patched = re.sub(r"CALL db\.index\.vector\.queryNodes\('candidate_embedding', \d+, \$queryVector\)", 
                         f"CALL db.index.vector.queryNodes('candidate_embedding', {top_v}, $queryVector)", current_text)
                         
        patched = re.sub(r"graph_results = graph_candidates\[:\d+\]", 
                         f"graph_results = graph_candidates[:{top_g}]", patched)
                         
        with open('jd_compiler.py', 'w', encoding='utf-8') as f:
            f.write(patched)
            
        print(f"Running NDCG benchmark...")
        output = subprocess.check_output(["python", "-X", "utf8", "test_ndcg_v8.py"], text=True, encoding="utf-8")
        
        ndcg_match = re.search(r"현재 측정값: ([\d\.]+)", output)
        ndcg = ndcg_match.group(1) if ndcg_match else "N/A"
        
        perf = re.search(r"완벽 검색\(1\.0\): (\d+)건\n부분 검색\(0<x<1\): (\d+)건\n검색 실패\(0\.0\): (\d+)건", output)
        perfect = perf.group(1) if perf else "N/A"
        partial = perf.group(2) if perf else "N/A"
        fail = perf.group(3) if perf else "N/A"
        
        rtl_state = "1.0" if "RTL Design SoC Integration DFT : [1" in output else "0.0" if "RTL Design SoC Integration DFT : [0" in output else "Other"
        ipo_state = "1.0" if "IPO IR AI : [1" in output else "0.0" if "IPO IR AI : [0" in output else "Other"
        
        results[name] = {
            "v": top_v, "g": top_g,
            "ndcg": ndcg,
            "perfect": perfect, "partial": partial, "fail": fail,
            "rtl": rtl_state, "ipo": ipo_state
        }
finally:
    # Always restore original text
    with open('jd_compiler.py', 'w', encoding='utf-8') as f:
        f.write(text)

print("==== SUMMARY ====")
print("조합 | Wv(Top_V) | Wg(Top_G) | NDCG   | 완벽 | 부분 | 실패 | RTL | IPO")
for name, data in results.items():
    print(f"{name:4} | {data['v']:^9} | {data['g']:^9} | {data['ndcg']:6} | {data['perfect']:^4} | {data['partial']:^4} | {data['fail']:^4} | {data['rtl']:^3} | {data['ipo']:^3}")
