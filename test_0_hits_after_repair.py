from jd_compiler import api_search_v8

QUERIES = [
    "FP&A 재무기획 시니어",
    "M&A 실사 경험 있는 재무팀장",
    "CTO 경험 있는 개발자",
    "Head of Marketing"
]

for q in QUERIES:
    res = api_search_v8(prompt=q)
    matched = res.get('matched', [])
    print(f"=====================================")
    print(f"쿼리: '{q}'")
    print(f"검색 결과: {len(matched)}명")
    if matched:
        print("Top 3 Candidate IDs:")
        for c in matched[:3]:
            # Debug candidate results
            print(f" - {c.get('이름', 'Unknown')} (Score: {c.get('_score', 0)})")
            mechanics_clean = str(c.get('_mechanics', '')).replace('<br>', ' | ').replace('<b>', '').replace('</b>', '')
            print(f"   => Mechanics: {mechanics_clean}")
