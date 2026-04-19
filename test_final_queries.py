from jd_compiler import api_search_v8
import json

queries = [
    "반도체 공정 엔지니어",
    "자동차 소프트웨어 개발자",
    "배터리 개발 연구원",
    "로봇 소프트웨어 엔지니어",
    "AI 반도체 설계"
]

results = []
print("=== Running Final Verification Queries ===")
for q in queries:
    try:
        res = api_search_v8(prompt=q)
        hits = len(res.get('matched', []))
        out = f"Query '{q}': {hits} hits"
        print(out)
        results.append(out)
    except Exception as e:
        out = f"Query '{q}': Error -> {e}"
        print(out)
        results.append(out)

with open("final_results_output.txt", "w", encoding="utf-8") as f:
    for r in results:
        f.write(r + "\n")
