from jd_compiler import parse_jd_to_json

queries = [
    "프론트엔드 개발자 React",
    "풀스택 개발자 스타트업",
    "iOS 개발자",
    "안드로이드 개발자",
    "그로스 마케터",
    "콘텐츠 마케터 SNS",
    "프로덕트 매니저 커머스",
    "UX 디자이너",
    "프로덕트 디자이너",
    "해외 영업",
    "HR 기획 보상 담당",
    "조직문화 담당자",
    "데이터 분석가 SQL",
    "데이터 사이언티스트",
]

with open("diag_output.txt", "w", encoding="utf-8") as f:
    for q in queries:
        try:
            result = parse_jd_to_json(q)
            f.write(f"쿼리: {q}\n")
            f.write(f"매핑 노드: {result.get('conditions', [])}\n\n")
        except Exception as e:
            f.write(f"쿼리: {q}\n")
            f.write(f"매핑 노드 ERROR: {e}\n\n")
