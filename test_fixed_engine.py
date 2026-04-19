from jd_compiler import api_search_v8

def run_real_verification():
    tests = [
        'Treasury Manager',
        'Framework Software Engineer',
        'Firmware Verification Engineer'
    ]
    
    for query in tests:
        print(f"\n========================================")
        print(f"🔍 API 실행: '{query}'")
        res = api_search_v8(prompt=query)
        matched = res.get('matched', [])
        
        print("👉 상위 5명 결과:")
        for i, c in enumerate(matched[:5], 1):
            name = c.get('name', 'Unknown')
            sc = c.get('score', 0)
            print(f"    {i}위. {name} (Score: {sc})")
    
if __name__ == '__main__':
    run_real_verification()
