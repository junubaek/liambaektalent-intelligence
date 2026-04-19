from jd_compiler import parse_jd_to_json

queries = [
    "FP&A 재무기획 시니어",
    "M&A 실사 경험 있는 재무팀장",
    "CTO 경험 있는 개발자",
    "Head of Marketing",
]

for q in queries:
    result = parse_jd_to_json(q)
    print(f"========================================")
    print(f"쿼리: {q}")
    print(f"매핑 결과: {result}")
