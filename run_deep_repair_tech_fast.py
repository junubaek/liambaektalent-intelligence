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
주어진 이력서에서 후보자가 수행한 [개발/데이터/디자인] 관련 행위를 상세히 추출하세요.

- action: 반드시 한정된 8개 동사 Enum 내에서만 선택하세요.
  * BUILT: 직접 코드 작성/시스템 구축
  * DESIGNED: 전략/조직/아키텍처/모델/디자인(UX) 기획 및 설계
  * MANAGED: 리딩, 총괄, 관리, 기존 시스템 운영
  * ANALYZED: 데이터 분석, 리서치
  * LAUNCHED: 서비스 출시
  * NEGOTIATED: 협상, 계약
  * GREW: 수치 성장
  * SUPPORTED: 실무 지원

- skill: 아래 5개 중에서만 선택하세요! (포함되지 않으면 절대 추출 불가)
  * Frontend_Development
  * Mobile_iOS
  * Android_Development
  * Data_Science_and_Analysis
  * UX_UI_Design

[중요] MANAGED 뿐만 아니라 실무진으로서의 역할(BUILT, DESIGNED, ANALYZED)을 적극적으로 추출하세요. 
"""

def extract(name, text):
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
        return json.loads(res.text).get("edges", [])
    except Exception as e:
        return []

def main():
    conn = sqlite3.connect("candidates.db")
    cursor = conn.cursor()
    cursor.execute("SELECT name_kr, raw_text FROM candidates WHERE raw_text IS NOT NULL")
    all_rows = cursor.fetchall()
    conn.close()

    RULES = {
        "Frontend_Development": ["프론트엔드", "frontend", "react", "리액트", "vue", "next.js", "typescript", "웹개발"],
        "Mobile_iOS": ["ios", "swift", "xcode", "아이폰 앱"],
        "Android_Development": ["안드로이드", "android", "kotlin", "java android"],
        "Data_Science_and_Analysis": ["데이터 분석", "데이터 사이언스", "sql", "python 분석", "머신러닝", "통계 분석", "tableau", "r 언어", "데이터 시각화"],
        "UX_UI_Design": ["ux", "ui", "figma", "프로덕트 디자인", "사용자 경험", "와이어프레임", "프로토타이핑", "사용자 조사", "ia"]
    }
    
    targets = {}
    for name, text in all_rows:
        text_lower = text.lower()
        matched = False
        for node, keywords in RULES.items():
            if any(k in text_lower for k in keywords):
                matched = True
                break
        if matched and name not in targets:
            targets[name] = text

    print(f"🎯 총 추출 대상 후보자: {len(targets)}명")
    
    edge_counts = defaultdict(int)
    
    with ThreadPoolExecutor(max_workers=20) as pool:
        futures = {pool.submit(extract, name, text): name for name, text in targets.items()}
        completed = 0
        with driver.session() as session:
            for fut in as_completed(futures):
                name = futures[fut]
                completed += 1
                edges = fut.result()
                if edges:
                    added_this = 0
                    for e in edges:
                        action = e["action"]
                        skill = e["skill"]
                        if skill not in RULES: continue
                        
                        session.run(f"MATCH (c:Candidate {{name_kr: $n}}) MERGE (s:Skill {{name: $s}}) MERGE (c)-[r:{action}]->(s)", n=name, s=skill)
                        added_this += 1
                        edge_counts[skill] += 1
                    if completed % 10 == 0:
                        print(f"[{completed}/{len(targets)}] {name} - {added_this}개 적재 완료")
                else:
                    if completed % 10 == 0:
                        print(f"[{completed}/{len(targets)}] {name} - 에러 또는 매핑 없음")

    print("\n✅ 최종 생성된 구출 엣지 통계:")
    for skill, cnt in edge_counts.items():
        print(f" - {skill}: {cnt} 엣지")
        
if __name__ == "__main__":
    main()
