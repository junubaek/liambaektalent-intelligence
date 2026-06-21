import sys, os, pickle
sys.stdout.reconfigure(encoding='utf-8')

with open('ontology_vectors.pkl', 'rb') as f:
    data = pickle.load(f)

print(f"총 노드 수: {len(data)}")
print(f"첫 번째 항목 구조: {list(data[0].keys())}")

# 샘플 몇 개
for item in data[:5]:
    node = item.get('node', item.get('name', '?'))
    vec = item.get('vector', item.get('embedding', []))
    print(f"  노드: {node}, 벡터 차원: {len(vec)}")

# 'vector' 키 vs 'embedding' 키?
print(f"\n키 확인: {list(data[0].keys())}")
