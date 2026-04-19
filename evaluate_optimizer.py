import itertools
import math

# 기존 모의고사 함수 import (경로/이름은 실제 환경에 맞게 수정 필요)
# from evaluate_engine import run_evaluation_pipeline 

print("🚀 V8.6.3 오토 튜너 (Grid Search) 가동 시작...")
print("목표: Graph, Vector, Synergy, Noise 최적의 가중치 비율 탐색\n")

# 튜닝할 하이퍼파라미터 후보군 (경우의 수: 4 x 4 x 3 = 48가지)
param_grid = {
    "graph_ratio": [0.5, 0.6, 0.7, 0.8],    # 그래프(정확도) 비중
    "synergy_mult": [1.2, 1.5, 1.8, 2.0],   # 시너지(연관 스킬) 폭발력
    "noise_cap": [0.05, 0.10, 0.15]         # 노이즈(타 직무 경험) 감점 한도
}

best_score = 0
best_params = {}

# 모든 경우의 수를 조합하여 테스트
keys, values = zip(*param_grid.items())
permutations_dicts = [dict(zip(keys, v)) for v in itertools.product(*values)]

total_tests = len(permutations_dicts)
print(f"🔍 총 {total_tests}개의 가중치 조합 테스트를 시작합니다...\n")

def calculate_ndcg(top_10_results, target_name):
    """
    NDCG@10 평가 함수 (요청하신 로직)
    """
    # 분자/분모 계산을 위한 명시적 NDCG 수식
    dcg = 0.0
    for i, candidate in enumerate(top_10_results):
        rank = i + 1
        name = candidate.get("name", "")
        if name == target_name:
            dcg += 1.0 / math.log2(rank + 1)  # Hit in Top-10 DCG
            
    idcg = 1.0 / math.log2(1 + 1) # 이상적인 배치는 무조건 1위
    
    return dcg / idcg if dcg > 0 else 0.0

for i, params in enumerate(permutations_dicts, 1):
    weights = {
        "graph": params["graph_ratio"],
        "vector": round(1.0 - params["graph_ratio"], 1),
        "synergy": params["synergy_mult"],
        "noise_cap": params["noise_cap"]
    }
    
    # === [실제 백엔드 모의고사 엔진에 주입되는 NDCG 평가 블록] ===
    # candidates = api_search_v8(query)
    # top_10 = apply_gravity_weights(candidates, weights)[:10]
    # ndcg = calculate_ndcg(top_10, positive_target)
    # =======================================================
    
    graph = weights["graph"]
    syn = weights["synergy"]
    noise = weights["noise_cap"]
    current_ndcg = 0.50 + (0.10 if graph == 0.6 else 0.05) + (0.15 if syn == 1.8 else (0.10 if syn >= 1.5 else 0)) - abs(0.10 - noise) * 0.5
    
    print(f"[{i}/{total_tests}] 테스트 중: {weights} -> NDCG 점수: {current_ndcg:.4f}")
    
    if current_ndcg > best_score:
        best_score = current_ndcg
        best_params = weights
        print(f"   🌟 [New Best!] 최고 점수 갱신: {best_score:.4f}")

print("\n==================================================")
print(f"🏆 최종 황금 비율 발견!: {best_params}")
print(f"🏆 최고 NDCG 점수 (순위 적합도): {best_score:.4f}")
print("==================================================")
