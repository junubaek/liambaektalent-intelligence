import time
from jd_compiler import api_search_v8

QUERIES = [
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

report = []
for q in QUERIES:
    try:
        res = api_search_v8(prompt=q)
        cnt = len(res.get('matched', []))
        report.append((q, cnt))
    except Exception as e:
        report.append((q, f"ERROR: {e}"))

print("=====================================")
print("쿼리 | 검색 결과 (명)")
print("---|---")
for q, cnt in report:
    print(f"{q} | {cnt}")
