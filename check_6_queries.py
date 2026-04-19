from jd_compiler import parse_jd_to_json
import time

queries = [
    "UI 디자이너",
    "스타트업 CFO",
    "콘텐츠 기획자",
    "인플루언서 마케터",
    "테크 리크루터",
    "엔터프라이즈 영업",
]

print("=== 6개 쿼리 parse_jd_to_json 매핑 결과 ===")
for q in queries:
    time.sleep(0.5)
    result = parse_jd_to_json(q)
    print(f"쿼리: {q}")
    print(f"조건: {result.get('conditions', [])}")
    print()
