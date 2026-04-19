import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import logging
from jd_compiler import api_search_v8

# Suppress detailed logs
logging.getLogger("jd_compiler").setLevel(logging.WARNING)

print("Running search against Neo4j with LIMIT 300...")
res = api_search_v8("IPO/펀딩 대비 자금 담당자 6년차")
matched = res.get("matched", [])

print(f"Total candidates returned from Neo4j (passing all conditions): {len(matched)}")

found_count = 0
for idx, c in enumerate(matched):
    name = c.get("name", "")
    if "대중" in name or "범기" in name:
        print(f"\n[{idx + 1}위] {name}")
        print(f"   Score: {c.get('score')}")
        print(f"   Edges: {c.get('matched_skills')}")
        found_count += 1

if found_count == 0:
    print("\n[!] 두 후보자 모두 300위 내에 존재하지 않거나 Mandatory 조건에서 탈락했습니다.")
