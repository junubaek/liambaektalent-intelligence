import sys
import os
import subprocess

sys.stdout.reconfigure(encoding='utf-8')
ROOT_DIR = r"c:\Users\cazam\Downloads\이력서자동분석검색시스템"
jd_path = os.path.join(ROOT_DIR, "jd_compiler.py")

with open(jd_path, "r", encoding="utf-8") as f:
    original_content = f.read()

combinations = [
    (0.3, 0.7), # Combo 1: Wv=0.3, Wg=0.7 (Graph 강세)
    (0.5, 0.5), # Combo 2: Wv=0.5, Wg=0.5 (균형)
    (0.6, 0.4)  # Combo 3: Wv=0.6, Wg=0.4 (Vector 강세)
]

def replace_weights(wv, wg):
    import re
    # We will replace ANY weights config that looks like weights = {'graph': X, 'vector': Y, 'synergy': 1.8, 'noise_cap': 0.10}
    # Using regex to find graph and vector values
    content = re.sub(
        r"weights\s*=\s*\{'graph':\s*[\d\.]+,\s*'vector':\s*[\d\.]+,\s*'synergy':\s*1\.8,\s*'noise_cap':\s*0\.1[0]?\}",
        f"weights = {{'graph': {wg}, 'vector': {wv}, 'synergy': 1.8, 'noise_cap': 0.10}}", 
        original_content
    )
    with open(jd_path, "w", encoding="utf-8") as f:
        f.write(content)

results = []
results.append("현재(0.4/0.6) : 0.2237")

for wv, wg in combinations:
    print(f"Testing Wv={wv}, Wg={wg} ...")
    replace_weights(wv, wg)
    
    res = subprocess.run(["python", "-X", "utf8", "test_ndcg_v8.py"], capture_output=True, text=True, encoding='utf-8')
    val = "ERROR"
    for line in res.stdout.split('\n'):
        if "- 현재 측정값:" in line:
            val = line.split(":")[1].strip()
            break
    
    print(f"Done Wv={wv}, Wg={wg}: {val}")
    results.append(f"조합 Wv={wv}/Wg={wg} : {val}")

with open("weight_results.txt", "w", encoding="utf-8") as rf:
    rf.write("\n".join(results))

# Restore original
with open(jd_path, "w", encoding="utf-8") as f:
    f.write(original_content)

print("\n[All Tests Completed!]")
for r in results:
    print(r)
