from jd_compiler import api_search_v8

queries = [
    "NPU 설계 엔지니어",
    "AI 반도체 아키텍처",
    "시스템 소프트웨어 엔지니어 NPU",
    "임베디드 리눅스 디바이스 드라이버",
    "AI 컴파일러 개발자",
    "LLM 추론 최적화",
    "GPGPU CUDA 개발자"
]

results_data = []

for query in queries:
    try:
        res = api_search_v8(query)
        matched = res.get("matched", [])
        
        top3 = []
        for c in matched[:3]:
            # Use exact keys mapped for the frontend
            name = c.get("이름", "N/A")
            comp = c.get("current_company", "미상")
            if not comp: comp = "미상"
            score = c.get("_score", 0)
            
            # Name masking
            if name and name != "N/A" and len(name) >= 2:
                masked = name[0] + "*" + (name[2:] if len(name)>2 else "")
            else:
                masked = name
                
            top3.append(f"{masked} ({comp}, {score:.1f})")
            
        if not top3:
            results_data.append((query, "0건 매칭", "-", "-"))
        else:
            while len(top3) < 3:
                top3.append("-")
            results_data.append((query, top3[0], top3[1], top3[2]))
    except Exception as e:
        results_data.append((query, "Error", str(e), ""))

output_lines = []
output_lines.append("| 쿼리명 | Top 1 | Top 2 | Top 3 |")
output_lines.append("|---|---|---|---|")
for row in results_data:
    output_lines.append(f"| {row[0]} | {row[1]} | {row[2]} | {row[3]} |")

with open("batch_results_table.md", "w", encoding="utf-8") as f:
    f.write("\n".join(output_lines))

print("Results written to batch_results_table.md")
