import json
import os
import collections

def extract_position_weights(golden_set_path):
    if not os.path.exists(golden_set_path):
        print(f"Error: {golden_set_path} not found.")
        return None

    with open(golden_set_path, 'r', encoding='utf-8') as f:
        dataset = json.load(f)

    # 포지션(Category)별 노드 분포 저장
    position_profiles = collections.defaultdict(lambda: collections.defaultdict(int))
    position_counts = collections.defaultdict(int)

    for item in dataset:
        category = item.get('category', 'General')
        target_nodes = item.get('target_nodes', [])
        
        position_counts[category] += 1
        for node in target_nodes:
            position_profiles[category][node] += 1

    # 가중치 행렬(Weight Matrix) 계산
    weight_matrix = {}
    for category, nodes in position_profiles.items():
        total_queries = position_counts[category]
        weights = {}
        for node, count in nodes.items():
            # 빈도가 높을수록 해당 포지션의 '필수 역량'으로 간주 (0.0 ~ 1.0)
            importance = count / total_queries
            # 최소 가중치 보정 (등장만 해도 어느 정도 가치가 있음)
            weights[node] = round(0.5 + (0.5 * importance), 2)
        
        weight_matrix[category] = weights

    return weight_matrix

if __name__ == "__main__":
    # v7 에이스 데이터셋에서 가중치 추출
    matrix_v7 = extract_position_weights('golden_dataset_v7.json')
    
    print("=== [v7 Ace Position Weight Matrix] ===")
    print(json.dumps(matrix_v7, indent=4, ensure_ascii=False))
    
    with open('position_weight_matrix.json', 'w', encoding='utf-8') as f:
        json.dump(matrix_v7, f, indent=4, ensure_ascii=False)
    print("\nWeight Matrix saved to position_weight_matrix.json")
