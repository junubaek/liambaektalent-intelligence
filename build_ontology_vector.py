import os
import re
import pickle
import numpy as np
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

import json

with open("secrets.json", "r", encoding="utf-8") as f:
    secrets = json.load(f)
client = OpenAI(api_key=secrets["OPENAI_API_KEY"])

def build_vector_map(output_pkl_path: str):
    print("1. ontology_graph에서 CANONICAL_MAP을 불러옵니다...")
    from ontology_graph import CANONICAL_MAP
    
    # 맵핑을 노드별로 그룹화
    node_synonyms = {}
    for alias, target in CANONICAL_MAP.items():
        if target not in node_synonyms:
            node_synonyms[target] = []
        node_synonyms[target].append(alias)
        
    ontology_data = []
    for node, aliases in node_synonyms.items():
        # 중복 제거 및 노드 본명도 포함
        aliases_set = set(aliases)
        aliases_set.add(node)
        context_string = f"{node}: " + ", ".join(aliases_set)
        
        ontology_data.append({
            "node": node,
            "context": context_string
        })
        
    print(f"총 {len(ontology_data)}개의 핵심 역량 노드 그룹화 완료. 임베딩을 시작합니다...")
        
    # OpenAI Batch Embedding 호출
    texts_to_embed = [item["context"] for item in ontology_data]
    
    # 100개씩 batch 처리하여 토큰 제한 회피
    all_embeddings = []
    batch_size = 100
    for i in range(0, len(texts_to_embed), batch_size):
        batch_texts = texts_to_embed[i:i+batch_size]
        response = client.embeddings.create(
            model="text-embedding-3-small",
            input=batch_texts
        )
        for emb_data in response.data:
            all_embeddings.append(emb_data.embedding)

    # 결과를 NumPy 배열로 변환하여 저장
    vector_map = []
    for idx, emb in enumerate(all_embeddings):
        vector_map.append({
            "node": ontology_data[idx]["node"],
            "vector": np.array(emb)
        })
        
    # PKL 파일로 저장
    with open(output_pkl_path, 'wb') as f:
        pickle.dump(vector_map, f)
        
    print(f"✅ 온톨로지 벡터 지도가 성공적으로 저장되었습니다: {output_pkl_path}")

if __name__ == "__main__":
    build_vector_map("ontology_vectors.pkl")
