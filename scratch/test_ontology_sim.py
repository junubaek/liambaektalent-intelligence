"""
Ontology Vector Index 사전 테스트
한국어 쿼리 ↔ 영어 노드 임베딩 유사도 확인
"""
import sys, os, pickle, json, math
sys.stdout.reconfigure(encoding='utf-8')

# OpenAI 클라이언트
from openai import OpenAI
with open('secrets.json', encoding='utf-8') as f:
    secrets = json.load(f)
client = OpenAI(api_key=secrets['OPENAI_API_KEY'])

# 온톨로지 벡터 로드
with open('ontology_vectors.pkl', 'rb') as f:
    raw = pickle.load(f)

nodes = [item['node'] for item in raw]
vecs  = [item['vector'] for item in raw]

print(f"온톨로지 노드 수: {len(nodes)}")
print(f"벡터 차원: {len(vecs[0])}")
print()

def get_embedding(text: str) -> list:
    res = client.embeddings.create(input=[text], model="text-embedding-3-small")
    return res.data[0].embedding

def cosine_sim(a, b) -> float:
    dot = sum(x*y for x,y in zip(a, b))
    na  = math.sqrt(sum(x*x for x in a))
    nb  = math.sqrt(sum(y*y for y in b))
    if na == 0 or nb == 0:
        return 0.0
    return dot / (na * nb)

# 테스트 쿼리 목록
test_queries = [
    # 반도체/AI 전문 쿼리
    "추론 가속화 전문가",
    "HBM 인터페이스 설계",
    "vLLM 최적화",
    "DRAM 아키텍처 설계",
    # 일반 쿼리
    "마케팅 퍼포먼스 그로스 해커",
    "B2B SaaS 영업 전략",
    "모바일 앱 프론트엔드 개발자",
    "재무 FP&A 예산 관리",
]

THRESHOLDS = [0.80, 0.75, 0.72, 0.70]

for query in test_queries:
    print("=" * 60)
    print(f"쿼리: {query}")
    print("-" * 60)

    q_vec = get_embedding(query)

    # 모든 노드와 유사도 계산
    sims = [(nodes[i], cosine_sim(q_vec, vecs[i])) for i in range(len(nodes))]
    sims.sort(key=lambda x: -x[1])

    # Top 10 출력
    print("Top-10 유사 노드:")
    for rank, (node, score) in enumerate(sims[:10], 1):
        bar = "★" if score >= 0.75 else ("○" if score >= 0.70 else "·")
        print(f"  {rank:2d}. [{score:.4f}] {bar} {node}")

    # threshold별 매칭 개수
    print()
    for thr in THRESHOLDS:
        cnt = sum(1 for _, s in sims if s >= thr)
        matched = [n for n, s in sims if s >= thr][:5]
        print(f"  threshold={thr}: {cnt}개 매칭 → {matched}")
    print()
