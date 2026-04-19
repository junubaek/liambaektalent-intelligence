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
주어진 이력서에서 후보자가 수행한 업무 관련 행위를 상세히 추출하세요.

- action: 반드시 한정된 8개 동사 Enum 내에서만 선택하세요.
  * BUILT: 직접 코드 작성/시스템 구축
  * DESIGNED: 전략/조직/아키텍처/모델/디자인 기획 및 설계
  * MANAGED: 리딩, 관리, 기존 시스템 운영
  * ANALYZED: 분석, 리서치
  * LAUNCHED: 출시
  * NEGOTIATED: 해외/국내 협상, 계약, 세일즈
  * GREW: 수치 (매출, 트래픽 등) 성장
  * SUPPORTED: 지원

- skill: 아래 9개 중에서만 선택하세요! (포함 안 되면 절대 추출 불가)
  * Frontend_Development
  * Mobile_iOS
  * Android_Development
  * Data_Science_and_Analysis
  * UX_UI_Design
  * Growth_Marketing
  * 해외영업
  * Organizational_Development
  * Fullstack_Development

[중요] MANAGED 뿐만 아니라 실무진, 지원진으로서의 역할(BUILT, DESIGNED, ANALYZED)을 적극적으로 추출하세요. 
"""

def extract(doc_hash, name, text):
    prompt = f"후보자명: {name}\n\n[이력서 본문]\n{text}"
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
        "Frontend_Development": ["프론트엔드", "frontend", "react", "vue", "next.js", "typescript", "리액트"],
        "Mobile_iOS": ["ios", "swift", "xcode", "아이폰 앱"],
        "Android_Development": ["안드로이드", "android", "kotlin"],
        "Data_Science_and_Analysis": ["데이터 분석", "sql", "머신러닝", "python 분석", "tableau", "통계"],
        "UX_UI_Design": ["ux", "figma", "프로덕트 디자인", "와이어프레임", "사용자 경험"],
        "Growth_Marketing": ["그로스", "growth hacking", "그로스해킹"],
        "해외영업": ["해외영업", "글로벌 영업", "수출", "해외 세일즈", "global sales"],
        "Organizational_Development": ["조직문화", "culture", "조직개발", "핵심가치", "리더십 교육"],
        "Fullstack_Development": ["풀스택", "fullstack", "full stack"]
    }

    conn = sqlite3.connect("candidates.db")
    cursor = conn.cursor()
    cursor.execute("SELECT document_hash, name_kr, raw_text FROM candidates WHERE raw_text IS NOT NULL")
    all_rows = cursor.fetchall()
    conn.close()

    # Deduplicate matching by hashing valid target
    targets = {}
    for doc_hash, name, text in all_rows:
        text_lower = text.lower()
        matched = False
        for node, keywords in RULES.items():
            if any(k in text_lower for k in keywords):
                matched = True
                break
        if matched and doc_hash not in targets:
            targets[doc_hash] = (name, text)

    print(f"🎯 총 추출 대상 후보자: {len(targets)}명")
    
    edge_counts = defaultdict(int)
    
    # 30 workers maximum speed
    with ThreadPoolExecutor(max_workers=30) as pool:
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
                        if skill not in RULES: continue
                        
                        # Use Neo4j candidate id which maps to document_hash
                        session.run(f"MATCH (c:Candidate {{id: $doc_hash}}) MERGE (s:Skill {{name: $s}}) MERGE (c)-[r:{action}]->(s)", doc_hash=doc_hash, s=skill)
                        added_this += 1
                        edge_counts[skill] += 1
                    if completed % 20 == 0:
                        print(f"[{completed}/{len(targets)}] {doc_hash[:8]} - {added_this}개 적재 완료")
                else:
                    if completed % 20 == 0:
                        print(f"[{completed}/{len(targets)}] {doc_hash[:8]} - 엣지 없음")

    print("\n✅ 최종 생성된 구출 엣지 통계:")
    for skill, cnt in edge_counts.items():
        print(f" - {skill}: {cnt} 엣지")
        
if __name__ == "__main__":
    main()
