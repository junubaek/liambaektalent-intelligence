import sqlite3
import json
import time
from collections import defaultdict
from google import genai
from pydantic import BaseModel
from enum import Enum
from neo4j import GraphDatabase
from concurrent.futures import ThreadPoolExecutor, as_completed

with open("secrets.json", "r", encoding="utf-8") as f:
    secrets = json.load(f)
client = genai.Client(api_key=secrets["GEMINI_API_KEY"])
driver = GraphDatabase.driver("neo4j://127.0.0.1:7687", auth=("neo4j", "toss1234"))

class ActionEnum(str, Enum):
    BUILT = "BUILT"
    DESIGNED = "DESIGNED"
    MANAGED = "MANAGED"
    ANALYZED = "ANALYZED"
    LAUNCHED = "LAUNCHED"
    NEGOTIATED = "NEGOTIATED"
    GREW = "GREW"
    SUPPORTED = "SUPPORTED"

class ParsedEdge(BaseModel):
    action: ActionEnum
    skill: str

class EdgeOutput(BaseModel):
    edges: list[ParsedEdge]

SYSTEM_INSTRUCTION = """
주어진 이력서에서 후보자가 수행한 업무 관련 행위를 추출하세요.

- action: 반드시 지정된 8개 동사 Enum 안에서만 선택하세요.
  * BUILT: 직접 코드 작성/시스템 구축
  * DESIGNED: 기획 및 설계
  * MANAGED: 리딩, 관리, 운영
  * ANALYZED: 분석, 리서치
  * LAUNCHED: 출시
  * NEGOTIATED: 협상, 세일즈
  * GREW: 수치 성장
  * SUPPORTED: 지원
- skill: 아래 3개 노드 중에서만 선택하세요! (포함 안 되면 추출 불가)
  * AI_Semiconductor_Architecture
  * System_Software
  * Sys_Software

이력서 내에 NPU, 런타임, 커널 최적화, 스케줄링, AI 가속기, Neural Engine 등의 내용이 있으면 위 노드들과 적극적으로 매핑해 주세요.
"""

def extract(doc_hash, name, text):
    # Only send first 5000 chars to save cost and speed up (sufficient for deep repair)
    prompt = f"후보자명: {name}\n\n[이력서 본문]\n{text[:5000]}"
    try:
        res = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config={
                "system_instruction": SYSTEM_INSTRUCTION,
                "response_mime_type": "application/json",
                "response_schema": EdgeOutput,
                "temperature": 0.1
            }
        )
        edges = json.loads(res.text).get("edges", [])
        return doc_hash, edges
    except Exception as e:
        return doc_hash, []

def main():
    conn = sqlite3.connect("candidates.db")
    cursor = conn.cursor()
    cursor.execute("""
        SELECT document_hash, name_kr, raw_text 
        FROM candidates 
        WHERE raw_text LIKE '%NPU%' OR (raw_text LIKE '%런타임%' AND raw_text LIKE '%커널%')
    """)
    all_rows = cursor.fetchall()
    conn.close()

    targets = {}
    for doc_hash, name, text in all_rows:
        if text and doc_hash not in targets:
            targets[doc_hash] = (name, text)

    print(f"🎯 총 추출 대상 후보자: {len(targets)}명 (NPU/런타임 해당자)")
    print(f"=========================================")

    edge_counts = defaultdict(int)

    # 30 workers maximum speed
    with ThreadPoolExecutor(max_workers=30) as executor:
        futures = {executor.submit(extract, h, v[0], v[1]): h for h, v in targets.items()}
        
        with driver.session() as session:
            for i, future in enumerate(as_completed(futures), 1):
                doc_hash = futures[future]
                try:
                    edges = future.result()
                    parsed = edges[1]
                    
                    if not parsed:
                        print(f"[{i}/{len(targets)}] {doc_hash[:8]} -> 추출된 엣지 없음")
                        continue
                        
                    inserted = 0
                    for edge in parsed:
                        action = edge['action']
                        skill = edge['skill']
                        # Valid set
                        if skill not in ["AI_Semiconductor_Architecture", "System_Software", "Sys_Software"]:
                            continue
                            
                        query = f"""
                        MATCH (c:Candidate {{id: '{doc_hash}'}})
                        MATCH (s:Skill {{name: '{skill}'}})
                        MERGE (c)-[r:{action}]->(s)
                        """
                        session.run(query)
                        inserted += 1
                        edge_counts[skill] += 1
                        
                    print(f"[{i}/{len(targets)}] {doc_hash[:8]} -> {inserted}개 엣지 생성 완료!")
                except Exception as e:
                    print(f"[{i}] Error: {e}")

    print("\n✅ Deep Repair Batch Completed!")
    print("Edge Distribution:")
    for k, v in edge_counts.items():
        print(f"  - {k}: {v} edges")

if __name__ == "__main__":
    main()
