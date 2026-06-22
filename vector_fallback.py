import os
import json
import pickle
import numpy as np
from numpy.linalg import norm
from openai import OpenAI

with open("secrets.json", "r", encoding="utf-8") as f:
    secrets = json.load(f)
client = OpenAI(api_key=secrets["OPENAI_API_KEY"])

# 1. 서버 구동 시 미리 메모리에 로드 (0.01초 소요, 매우 가벼움)
try:
    with open("ontology_vectors.pkl", 'rb') as f:
        ONTOLOGY_VECTORS = pickle.load(f)
except FileNotFoundError:
    print("⚠️ ontology_vectors.pkl 파일이 없습니다. build_ontology_vector.py를 먼저 실행하세요.")
    ONTOLOGY_VECTORS = []

def get_closest_node(user_keyword: str, threshold: float = 0.45):
    """
    [L2 Fallback] 벡터 공간에서 가장 유사한 표준 노드를 반환합니다.
    """
    # 1. 유저 키워드를 벡터로 변환
    res = client.embeddings.create(
        model="text-embedding-3-small",
        input=user_keyword
    )
    query_vector = np.array(res.data[0].embedding)
    
    best_node = None
    best_score = -1.0
    
    # 2. 491개 노드와 유사도 전수 비교 (0.001초 이내)
    for item in ONTOLOGY_VECTORS:
        score = np.dot(query_vector, item["vector"]) / (norm(query_vector) * norm(item["vector"]))
        if score > best_score:
            best_score = score
            best_node = item["node"]
            
    # 3. 임계치(Threshold) 통과 여부 확인
    if best_score >= threshold:
        print(f"💡 [Vector Fallback] '{user_keyword}' ➔ '{best_node}' (유사도: {best_score:.3f})")
        return best_node
    else:
        print(f"❌ [Vector Fallback Fail] '{user_keyword}' (최고 유사도: {best_score:.3f} - 임계치 미달)")
        return None
