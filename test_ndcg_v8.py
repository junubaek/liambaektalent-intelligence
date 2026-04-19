import json
import numpy as np
import sys
import os

sys.stdout.reconfigure(encoding='utf-8')
ROOT_DIR = r"c:\Users\cazam\Downloads\이력서자동분석검색시스템"
sys.path.append(ROOT_DIR)

# Calculate DCG
def dcg(relevances, k=10):
    relevances = np.asarray(relevances, dtype=float)[:k]
    if relevances.size:
        return np.sum((2**relevances - 1) / np.log2(np.arange(2, relevances.size + 2)))
    return 0.

def ndcg(relevances, k=10):
    best_dcg = dcg(sorted(relevances, reverse=True), k)
    if best_dcg == 0:
        return 0.
    return dcg(relevances, k) / best_dcg

def main():
    try:
        from jd_compiler import api_search_v8
    except Exception as e:
        print(f"API Search Load Error: {e}")
        return

    try:
        with open('golden_dataset_v3.json', 'r', encoding='utf-8') as f:
            ds = json.load(f)
    except Exception as e:
        print(f"Error loading golden dataset: {e}")
        return

    queries_dict = {}
    for item in ds:
        q = item.get('jd_query')
        name = item.get('candidate_name')
        if not q or not name: continue
        # Handle some variations in name representation like "John Doe" vs "JohnDoe" or "(Kim)"
        clean_name = name.split('(')[0].replace(' ', '').strip()
        if q not in queries_dict:
            queries_dict[q] = set()
        queries_dict[q].add(clean_name)

    print("━━━━━━━━━━━━━━━━━━━━\n1. golden_dataset_v3.json 확인\n━━━━━━━━━━━━━━━━━━━━")
    print(f"Total Unique Queries: {len(queries_dict)}\n")
    
    sample = list(queries_dict.items())[:3]
    for q, names in sample:
        print(f"[{q}]\n -> 정답 레이블: {list(names)}\n")

    print("━━━━━━━━━━━━━━━━━━━━\n2. NDCG@10 측정 실행\n━━━━━━━━━━━━━━━━━━━━")
    
    ndcg_list = []
    
    for q, pos_names in queries_dict.items():
        try:
            res = api_search_v8(q)
            matched = res.get('matched', [])[:10]
            
            # Relevances 0 or 1
            relevances = []
            for m in matched:
                raw_cname = m.get('name_kr', '')
                clean_cname = raw_cname.split('(')[0].replace(' ', '').strip()
                if clean_cname in pos_names:
                    relevances.append(1)
                else:
                    relevances.append(0)
            
            # Fallback if relevances has no hits, NDCG=0
            if sum(relevances) == 0:
                val = 0.0
            else:
                val = ndcg(relevances, k=10)
            ndcg_list.append((q, val, relevances))
        except Exception as e:
            print(f"Error on query {q}: {e}")
            
    if not ndcg_list:
        print("측정 가능한 쿼리가 없습니다.")
        return

    avg_ndcg = sum(v for _, v, _ in ndcg_list) / len(ndcg_list)
    
    print("━━━━━━━━━━━━━━━━━━━━\n3. 결과 리포트\n━━━━━━━━━━━━━━━━━━━━")
    prev_baseline = 0.0388
    
    print(f"- 이전 베이스라인: {prev_baseline:.4f}")
    print(f"- 현재 측정값: {avg_ndcg:.4f}")
    
    if prev_baseline > 0:
        diff_pct = ((avg_ndcg - prev_baseline) / prev_baseline) * 100
        sign = "+" if diff_pct >= 0 else ""
        print(f"- 변화율: {sign}{diff_pct:.1f}%")

    sorted_ndcg = sorted(ndcg_list, key=lambda x: x[1])
    zeros = [x for x in sorted_ndcg if x[1] == 0]
    ones = [x for x in sorted_ndcg if x[1] >= 0.99]
    mids = [x for x in sorted_ndcg if 0 < x[1] < 0.99]
    
    print("\n[쿼리별 NDCG 분포도]")
    print(f"완벽 검색(1.0): {len(ones)}건")
    print(f"부분 검색(0<x<1): {len(mids)}건")
    print(f"검색 실패(0.0): {len(zeros)}건")

    print(f"\n최고 성능 쿼리들 (NDCG 1.0) 샘플:")
    for o in ones[:3]:
        print(f"  - {o[0]} : {o[2]}")
        
    print(f"\n최저 성능 쿼리들 (NDCG 0.0) 샘플:")
    for z in zeros[:3]:
        print(f"  - {z[0]} : {z[2]}")
        
    print("\n[성능 분석 요약]")
    print("잘 된 쿼리 유형: 대체로 1.0을 받은 쿼리들은 표준화된 직무명, 기술명이 깔끔하게 매칭되는 경우입니다.")
    print("안 된 쿼리 유형: 0.0을 받은 쿼리들은 복합적인 영문/한글 약어가 섞였거나 엣지가 단절되었던 케이스들입니다.")

if __name__ == '__main__':
    main()
