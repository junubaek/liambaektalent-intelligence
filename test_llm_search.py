from jd_compiler import api_search_v8

query = "LLM 엔지니어"

print("🔍 검색 쿼리 테스트 시작")
print(f"\n==============================================")
print(f"📌 Query: {query}")
try:
    results = api_search_v8(query)
    candidates = results.get("matched", [])
    print(f"✅ 검색 결과: 총 {len(candidates)}명 매칭")
    if candidates:
        for i, c in enumerate(candidates[:10]):
            score = c.get('total_score', c.get('score', 0))
            print(f"  {i+1}. {c.get('name', c.get('name_kr', 'N/A'))} (Score: {score}) - {c.get('matched_raw', [])}")
except Exception as e:
    import traceback
    print(f"❌ 검색 에러: {e}")
    traceback.print_exc()

print(f"\n==============================================")
print("테스트 완료")
