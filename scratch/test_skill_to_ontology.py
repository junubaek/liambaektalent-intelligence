"""
검증: parse_jd_with_llm의 skills 필드를 임베딩해서 온톨로지 노드와 매칭
추가 LLM 호출 없이 동작하는지 확인
"""
import sys, os, pickle, json, math
sys.stdout.reconfigure(encoding='utf-8')

from openai import OpenAI
with open('secrets.json', encoding='utf-8') as f:
    secrets = json.load(f)
client = OpenAI(api_key=secrets['OPENAI_API_KEY'])

# 온톨로지 벡터 로드
with open('ontology_vectors.pkl', 'rb') as f:
    raw = pickle.load(f)
nodes = [item['node'] for item in raw]
vecs  = [item['vector'] for item in raw]

# jd_compiler에서 parse_jd_with_llm 가져오기
sys.path.insert(0, '.')
from jd_compiler import parse_jd_with_llm

def get_embedding(text: str) -> list:
    res = client.embeddings.create(input=[text], model="text-embedding-3-small")
    return res.data[0].embedding

def cosine_sim(a, b) -> float:
    dot = sum(x*y for x,y in zip(a, b))
    na  = math.sqrt(sum(x*x for x in a))
    nb  = math.sqrt(sum(y*y for y in b))
    return dot / (na * nb) if na and nb else 0.0

def ontology_search_via_skill(skill_text: str, threshold=0.75, top_k=5):
    """스킬명 임베딩 → 온톨로지 노드 유사도 검색"""
    skill_vec = get_embedding(skill_text)
    sims = [(nodes[i], cosine_sim(skill_vec, vecs[i])) for i in range(len(nodes))]
    sims.sort(key=lambda x: -x[1])
    return [(n, s) for n, s in sims[:top_k] if s >= threshold]

# 테스트 쿼리
test_queries = [
    "추론 가속화 전문가",
    "HBM 인터페이스 설계",
    "vLLM 최적화",
    "DRAM 아키텍처 설계",
    "마케팅 퍼포먼스 그로스 해커",
    "B2B SaaS 영업 전략",
    "모바일 앱 프론트엔드 개발자",
]

THRESHOLD = 0.75

for query in test_queries:
    print("=" * 65)
    print(f"쿼리: {query}")

    # Step 1: LLM으로 skills 추출
    llm_result = parse_jd_with_llm(query, client)
    llm_skills = llm_result.get('skills', [])
    print(f"LLM 추출 skills: {llm_skills}")

    # Step 2: 각 skill을 임베딩 → 온톨로지 매칭
    all_matched = {}
    for skill in llm_skills:
        matched = ontology_search_via_skill(skill, threshold=THRESHOLD, top_k=5)
        if matched:
            print(f"  [{skill}] → {[(n, round(s, 4)) for n, s in matched]}")
            for n, s in matched:
                if n not in all_matched or all_matched[n] < s:
                    all_matched[n] = s
        else:
            # threshold 낮춰서 top-1만 확인
            best = ontology_search_via_skill(skill, threshold=0.0, top_k=1)
            if best:
                print(f"  [{skill}] → 미매칭 (최고: {best[0][0]} {best[0][1]:.4f})")
            else:
                print(f"  [{skill}] → 미매칭")

    if all_matched:
        final_nodes = sorted(all_matched.items(), key=lambda x: -x[1])
        print(f"최종 추가될 온톨로지 노드: {[n for n, _ in final_nodes]}")
    else:
        print(f"최종 추가될 온톨로지 노드: 없음")
    print()
