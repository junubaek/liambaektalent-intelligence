from jd_compiler import api_search_v8
import json
import time

def test_hong_and_stats():
    # 1. 홍기재 타겟 검색
    q = 'vllm kubernetes llm serving'
    print(f"🔍 API 실행: '{q}'")
    st = time.time()
    res = api_search_v8(q)
    matched = res.get('matched', [])
    
    print("\n👉 상위 10명 결과:")
    target_rank = -1
    for i, r in enumerate(matched[:10]):
        rank = i + 1
        name = r.get('name') or '미상'
        score = r.get('score', 0)
        print(f"    {rank}위. {name} (Score: {score})")
        if '홍기재' in name:
            target_rank = rank
            
    if target_rank == -1:
        # 10위 밖인지 확인
        for i, r in enumerate(matched):
            if '홍기재' in (r.get('name') or ''):
                target_rank = i + 1
                break
                
    print(f"\n🎯 [테스트 완료] 타겟(홍기재) 최종 등수: {target_rank if target_rank != -1 else '50위 밖'}\n")
    
    # 2. 비용/시간 계산
    processed_file = 'processed.json'
    try:
        with open(processed_file, 'r', encoding='utf-8') as f:
            processed = json.load(f)
            total_count = len(processed)
    except:
        total_count = 3345 # approximate fallback
        
    print(f"📊 [전체 재파싱 예상 견적]")
    print(f"- 대상 인원: 총 {total_count}명")
    
    # 시간: 1배치(5명) 당 약 35초 (과거 로그 기준 33.6초)
    batch_size = 5
    batch_time_sec = 35 
    total_batches = (total_count + batch_size - 1) // batch_size
    total_time_sec = total_batches * batch_time_sec
    total_time_hrs = total_time_sec / 3600
    
    print(f"- 소요 시간: 약 {total_time_hrs:.1f}시간 ({total_batches} 배치 * 35초)")
    
    # 비용: Gemini 1.5 Flash 기준 (현 dynamic_parser.py model)
    # 입력: 이력서 당 약 500토큰 -> 배치당 2500토큰. 프롬프트 약 500토큰. = 3000 Tokens/batch
    # 출력: 배치당 약 200 토큰.
    # $0.075 / 1M input, $0.3 / 1M output
    total_input_tokens = total_batches * 3000
    total_output_tokens = total_batches * 250
    input_cost = (total_input_tokens / 1_000_000) * 0.075
    output_cost = (total_output_tokens / 1_000_000) * 0.30
    total_cost_usd = input_cost + output_cost
    
    print(f"- 예상 API 비용: 약 ${total_cost_usd:.4f} USD (입력 {total_input_tokens:,}토큰 + 출력 {total_output_tokens:,}토큰)")

if __name__ == '__main__':
    test_hong_and_stats()
