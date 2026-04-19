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
  * NEGOTIATED: 해외/국내 협상, 계약, 세일즈, 고객대응, 소싱
  * GREW: 수치 (매출, 트래픽 등) 성장
  * SUPPORTED: 지원

- skill: 아래 11개 노드 중에서만 선택하세요! (포함 안 되면 절대 추출 불가)
  * Credit_Analysis
  * Financial_Regulation
  * Regulatory_Affairs
  * Medical_Device
  * Video_Production
  * Content_Marketing
  * Commerce_MD
  * Procurement_Buyer
  * Architecture_Design
  * Interior_Design
  * Global_HR
  * Graphic_Design
  * Patent_Management

[중요] MANAGED 뿐만 아니라 실무진, 전문분야 담당자로서의 역할(ANALYZED, DESIGNED, NEGOTIATED)을 적극적으로 추출하세요. 
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
        "Credit_Analysis": ["신용분석", "여신", "신용평가"],
        "Financial_Regulation": ["금융규제", "금감원", "금융당국"],
        "Regulatory_Affairs": ["인허가", "ra", "허가"],
        "Medical_Device": ["의료기기", "medical device"],
        "Video_Production": ["pd", "연출", "영상 제작", "유튜브", "youtube"],
        "Content_Marketing": ["시나리오", "스크립트", "각본"],
        "Graphic_Design": ["웹툰", "만화"],
        "Commerce_MD": ["식품", "식품md"],
        "Procurement_Buyer": ["구매", "바이어", "소싱"],
        "Architecture_Design": ["건축", "설계사"],
        "Interior_Design": ["인테리어", "interior"],
        "Global_HR": ["글로벌 hr", "global hr", "해외 인사"],
        "Patent_Management": ["특허"]
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
    print(f"=========================================")
    
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

    print("\n✅ 최종 생성된 구출 엣지 통계 (Round 4):")
    
    summary_md = "| Node Name | Neo4j Added Edges |\n|:---|---:|\n"
    for skill, cnt in edge_counts.items():
        print(f" - {skill}: {cnt} 엣지")
        summary_md += f"| {skill} | {cnt} |\n"
        
    with open("round4_deep_repair_results.md", "w", encoding="utf-8") as f:
        f.write("# Round 4 Deep Repair Edge Counts\n\n")
        f.write(summary_md)
        
if __name__ == "__main__":
    main()
