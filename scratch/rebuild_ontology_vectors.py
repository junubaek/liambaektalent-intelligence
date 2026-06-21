"""
온톨로지 노드 벡터 재생성: 노드명 단독으로 임베딩
기존 방식: "NodeName: alias1, alias2, ..." (컨텍스트 길어서 단어와 유사도 낮음)
신규 방식: "NodeName" 단독 → 짧은 스킬명과 직접 비교 가능
"""
import sys, os, pickle, json, math, time
sys.stdout.reconfigure(encoding='utf-8')
import numpy as np

from openai import OpenAI
with open('secrets.json', encoding='utf-8') as f:
    secrets = json.load(f)
client = OpenAI(api_key=secrets['OPENAI_API_KEY'])

# CANONICAL_MAP에서 고유 노드 추출
sys.path.insert(0, '.')
from jd_compiler import CANONICAL_MAP

nodes = sorted(set(CANONICAL_MAP.values()))
print(f"고유 노드 수: {len(nodes)}")

# 배치 임베딩 (100개씩)
all_vecs = []
batch_size = 100
for i in range(0, len(nodes), batch_size):
    batch = nodes[i:i+batch_size]
    resp = client.embeddings.create(
        model="text-embedding-3-small",
        input=batch
    )
    for d in resp.data:
        all_vecs.append(np.array(d.embedding))
    print(f"  {min(i+batch_size, len(nodes))}/{len(nodes)} 완료...")
    time.sleep(0.1)  # rate limit 방지

# 저장 (기존 파일 백업 후 교체)
import shutil
if os.path.exists('ontology_vectors.pkl'):
    shutil.copy('ontology_vectors.pkl', 'ontology_vectors_backup_contextual.pkl')
    print("기존 파일 백업: ontology_vectors_backup_contextual.pkl")

vector_map = [{'node': nodes[i], 'vector': all_vecs[i]} for i in range(len(nodes))]
with open('ontology_vectors.pkl', 'wb') as f:
    pickle.dump(vector_map, f)

print(f"\n재생성 완료: {len(vector_map)}개 노드, {len(all_vecs[0])}차원")
print(f"저장: ontology_vectors.pkl")

# 빠른 검증: "Marketing" 검색
matrix = np.array([v['vector'] for v in vector_map])
matrix_norm = matrix / np.linalg.norm(matrix, axis=1, keepdims=True)

test_skills = ["Marketing", "Frontend", "LLM_Inference", "Backend", "Architecture_Design"]
for skill in test_skills:
    resp = client.embeddings.create(model="text-embedding-3-small", input=[skill])
    q_vec = np.array(resp.data[0].embedding)
    q_vec = q_vec / np.linalg.norm(q_vec)
    sims = matrix_norm @ q_vec
    top_idx = np.argsort(-sims)[:5]
    top = [(nodes[i], float(sims[i])) for i in top_idx]
    print(f"\n'{skill}' 검색 결과:")
    for n, s in top:
        bar = "✅" if s >= 0.80 else ("○" if s >= 0.75 else "·")
        print(f"  {bar} [{s:.4f}] {n}")
