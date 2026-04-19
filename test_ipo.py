import sys
import jd_compiler

query = "IPO/펀딩 을 대비하여 자금 담당자를 찾고있어. 최소 6년차 이상의 경력자를 찾아줘"

print("="*60)
print("[Phase 1] Extracted Intention (JSON):")
conds = jd_compiler.parse_jd_to_json(query)
print(conds)

print("\n[Phase 2] Executing Vector Prefilter (TF-IDF)...")
top_names = jd_compiler.prefilter_candidates(query, num_candidates=300)
print(f"Top 5 names: {top_names[:5]}")

print("\n[Phase 3] Executing Neo4j OPTIONAL MATCH Score calculation...")
results = jd_compiler.opt_match_score(top_names, conds)
print(f"Final Count: {len(results)}")
for c in results[:5]:
    print(c)
