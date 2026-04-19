import sqlite3
import json
from collections import defaultdict
from pydantic import BaseModel
from enum import Enum
from neo4j import GraphDatabase
from concurrent.futures import ThreadPoolExecutor, as_completed

with open("secrets.json", "r", encoding="utf-8") as f:
    secrets = json.load(f)

# Use original genai directly using the pattern from round 4
from google import genai
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
주어진 이력서에서 후보자가 수행한 업무 관련 행위를 상세히 추출하세요.

- action: 반드시 한정된 8개 동사 Enum 내에서만 선택하세요. (BUILT, DESIGNED, MANAGED, ANALYZED, LAUNCHED, NEGOTIATED, GREW, SUPPORTED)
- skill: 아래 1개 노드 중에서만 선택하세요! (포함 안 되면 절대 추출 불가)
  * LLM_Engineering

[중요] LLM(거대언어모델), RAG 구축, LLM Fine-tuning(파인튜닝), 프롬프트 엔지니어링, LangChain, LlamaIndex, ChatGPT API 등을 다룬 이력이 있다면 적절한 action(주로 BUILT, DESIGNED, ANALYZED)과 함께 매핑하세요.
"""

def extract(doc_hash, name, text):
    prompt = f"후보자명: {name}\\n\\n[이력서 본문]\\n{text}"
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
    RULES = {
        "LLM_Engineering": [
            "llm", "rag", "fine-tuning", "파인튜닝",
            "langchain", "llamaindex", "거대언어모델",
            "프롬프트 엔지니어링", "chatgpt api", "프롬프트", "prompt"
        ]
    }

    conn = sqlite3.connect("candidates.db")
    cursor = conn.cursor()
    cursor.execute("SELECT document_hash, name_kr, raw_text FROM candidates WHERE raw_text IS NOT NULL")
    all_rows = cursor.fetchall()
    conn.close()

    targets = {}
    for doc_hash, name, text in all_rows:
        text_lower = text.lower()
        matched = False
        for k in RULES["LLM_Engineering"]:
            if k in text_lower:
                matched = True
                break
        if matched and doc_hash not in targets:
            targets[doc_hash] = (name, text)

    print(f"🎯 총 추출 대상 후보자: {len(targets)}명")
    print(f"=========================================")
    
    edge_counts = defaultdict(int)
    
    with ThreadPoolExecutor(max_workers=10) as pool:
        futures = []
        for doc_hash, val in targets.items():
            futures.append(pool.submit(extract, doc_hash, val[0], val[1]))
            
        completed = 0
        with driver.session() as session:
            for fut in as_completed(futures):
                completed += 1
                doc_hash, edges = fut.result()
                if edges:
                    added_this = 0
                    for e in edges:
                        action = e["action"]
                        skill = e["skill"]
                        if skill != "LLM_Engineering": continue
                        
                        session.run(f"MATCH (c:Candidate {{id: $doc_hash}}) MERGE (s:Skill {{name: $s}}) MERGE (c)-[r:{action}]->(s)", doc_hash=doc_hash, s=skill)
                        added_this += 1
                        edge_counts[skill] += 1
                        
                    if added_this > 0:
                        print(f"[{completed}/{len(targets)}] {doc_hash[:8]} - {added_this}개 적재 완료")
                else:
                    if completed % 10 == 0:
                        print(f"[{completed}/{len(targets)}] {doc_hash[:8]} - 진행중...")

    print("\\n✅ 최종 생성된 구출 엣지 통계 (LLM):")
    for skill, cnt in edge_counts.items():
        print(f" - {skill}: {cnt} 엣지")
        
if __name__ == "__main__":
    main()
