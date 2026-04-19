import json
import math
from jd_compiler import api_search_v8
import logging

# API 내부 로깅 억제 (깔끔한 출력을 위해)
logging.getLogger('jd_compiler').setLevel(logging.ERROR)

def run_real_evaluation():
    try:
        with open('golden_dataset_v4.json', 'r', encoding='utf-8') as f:
            golden = json.load(f)
    except Exception as e:
        print(f"Dataset load error: {e}")
        return

    positives = [i for i in golden if i['label'] == 'positive']
    total_cases = len(positives)
    
    hits = []
    misses = []
    total_ndcg = 0.0
    
    print(f"🚀 V8.6.3 순수 엔진 NDCG@10 실시간 평가 시작 (총 {total_cases}건)...\n")
    
    for idx, item in enumerate(positives, 1):
        query = item['jd_query']
        target = item['candidate_name']
        
        try:
            res = api_search_v8(prompt=query)
        except Exception as e:
            print(f"Error on query '{query}': {e}")
            misses.append(target)
            continue
            
        matched = res.get('matched', []) if isinstance(res, dict) else res
        top10 = matched[:10]
        
        hit_rank = -1
        for i, c in enumerate(top10):
            # 엔진 변경 후 c.get('name') 에 실제 이름이 매핑되어 있음 확인
            name = c.get('name', 'Unknown')
            if name == target:
                hit_rank = i + 1
                break
                
        if hit_rank != -1:
            dcg = 1.0 / math.log2(hit_rank + 1)
            idcg = 1.0 / math.log2(1 + 1)
            ndcg = dcg / idcg
            total_ndcg += ndcg
            hits.append(target)
            print(f"[{idx}/{total_cases}] ✅ {target:<10} | Rank {hit_rank:<2} | Query: {query}")
        else:
            misses.append(target)
            print(f"[{idx}/{total_cases}] ❌ {target:<10} | Missed    | Query: {query}")

    avg_ndcg = total_ndcg / total_cases if total_cases > 0 else 0
    
    print("\n" + "="*50)
    print("🏆 실시간 엔진 NDCG 평가 결과 보고 (포장 없음)")
    print("="*50)
    print(f"1. 평균 NDCG@10     : {avg_ndcg:.4f}")
    print(f"2. Top-10 히트 건수 : {len(hits)} / {total_cases}")
    
    unique_hits = sorted(list(set(hits)))
    print(f"\n3. 히트된 후보자 목록 ({len(unique_hits)}명)")
    print("    " + ", ".join(unique_hits))
    
    tech_keywords = ['SQL', 'DB', 'Backend', 'Frontend', 'React', 'iOS', 'Android', 'vLLM', 'PyTorch', 'C++', 'Java', 'Python', 'Go', 'Data', 'Machine', 'Learning', 'AI', 'Cloud', 'Infrastructure', 'AWS', 'Network', 'Security', 'DevOps', 'QA']
    
    tech_misses = []
    non_tech_misses = []
    seen_misses = set()
    
    for item in positives:
        t = item['candidate_name']
        if t in misses and t not in seen_misses:
            seen_misses.add(t)
            q = item['jd_query'].lower()
            if any(tk.lower() in q for tk in tech_keywords):
                tech_misses.append(f"{t} ({item['jd_query']})")
            else:
                non_tech_misses.append(f"{t} ({item['jd_query']})")
                
    tech_misses.sort()
    non_tech_misses.sort()

    print(f"\n4. 미발견 케이스 목록 ({len(seen_misses)}명)")
    print(f"   [기술직 미발견] ({len(tech_misses)}명)")
    for tm in tech_misses:
        print(f"    - {tm}")
        
    print(f"\n   [비기술직 미발견] ({len(non_tech_misses)}명)")
    for ntm in non_tech_misses:
        print(f"    - {ntm}")
    print("="*50)

if __name__ == '__main__':
    run_real_evaluation()
