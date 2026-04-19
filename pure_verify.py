from jd_compiler import api_search_v8

def pure_verify():
    print("🚀 순수 실시간 V8 API 호출 검증\n")
    queries = [
        "Financial Systems Manager",
        "Framework Software Engineer"
    ]
    
    for q in queries:
        print("="*60)
        print(f"🔍 API 직접 호출: '{q}'")
        # 오직 순수 api_search_v8 만 호출합니다 (어떤 외부 개입도 없음)
        res = api_search_v8(prompt=q)
        matched = res.get('matched', [])
        
        print(f"👉 순수 Top-10 출력 결과:")
        for i, c in enumerate(matched[:10], 1):
            name = c.get('name', 'Unknown')
            score = c.get('score', 0)
            print(f"    {i}위. {name} (Score: {score})")
            
if __name__ == "__main__":
    pure_verify()
