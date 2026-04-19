import sqlite3
import json
import time
from google import genai
from pydantic import BaseModel
from enum import Enum
from neo4j import GraphDatabase
from concurrent.futures import ThreadPoolExecutor, as_completed

with open("secrets.json", "r", encoding="utf-8") as f:
    secrets = json.load(f)
GEMINI_API_KEY = secrets["GEMINI_API_KEY"]
NEO4J_URI = "neo4j://127.0.0.1:7687"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "toss1234"

client = genai.Client(api_key=GEMINI_API_KEY)
driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))

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
이력서 텍스트에서 후보자가 실무에서 수행한 [재무/투자/기획] 관련 행위를 상세히 추출합니다.

- action: 반드시 한정된 8개 동사 Enum 내에서만 선택하세요.
  * BUILT: 직접 코드 작성/시스템 구축
  * DESIGNED: 전략/조직/아키텍처/모델 기획 및 설계
  * MANAGED: 리딩, 총괄, 관리, 기존 시스템 운영
  * ANALYZED: 데이터 분석, 실사(Due Diligence), 리서치, 가치평가(Valuation)
  * LAUNCHED: 서비스 출시
  * NEGOTIATED: 협상, 피칭, 계약 체결
  * GREW: 수치 성장
  * SUPPORTED: 주도적 책임이 아닌 일부 참여/실무 지원

- skill: 아래 2개 중에서만 선택하세요!
  * Financial_Planning_and_Analysis: FP&A, 재무기획, 경영분석, 예산 편성/재무모델/Variance 분석
  * Mergers_and_Acquisitions: M&A 인수합병 전략, 타겟 발굴, 기업가치평가, 실사(Due Diligence), PMI 프로세스

[매우 중요한 주의사항]
팀장급이 아니더라도 실무진으로 실사나 모델링에 참여했다면 ANALYZED, SUPPORTED, DESIGNED 등의 액션을 반드시 포함하세요. (MANAGED만 뽑지 마세요)
"""

def process_candidate(row):
    name = row["name_kr"]
    text = row["raw_text"]
    if not text: return name, []
    
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
        parsed = json.loads(res.text)
        return name, parsed.get("edges", [])
    except Exception as e:
        return name, []

def process_deep_repair():
    conn = sqlite3.connect("candidates.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("""
        SELECT name_kr, raw_text FROM candidates 
        WHERE raw_text LIKE '%FP&A%' OR raw_text LIKE '%재무기획%' OR raw_text LIKE '%경영분석%' 
           OR raw_text LIKE '%예산관리%' OR raw_text LIKE '%Variance Analysis%'
           OR raw_text LIKE '%M&A%' OR raw_text LIKE '%인수합병%' OR raw_text LIKE '%실사%'
           OR raw_text LIKE '%Due Diligence%' OR raw_text LIKE '%PMI%'
    """)
    rows = cursor.fetchall()
    conn.close()
    
    print(f"🎯 딥 리페어 대상 후보자 수: {len(rows)}명")
    
    with driver.session() as session:
        # Use ThreadPool
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(process_candidate, dict(row)) for row in rows]
            
            completed = 0
            for future in as_completed(futures):
                completed += 1
                name, edges = future.result()
                
                if not edges:
                    print(f"[{completed}/{len(rows)}] {name} - 엣지 없음")
                    continue
                
                valid_skills = ["Financial_Planning_and_Analysis", "Mergers_and_Acquisitions"]
                added_count = 0
                
                for e in edges:
                    action = e["action"]
                    skill = e["skill"]
                    if skill not in valid_skills: continue
                    
                    query = f"""
                    MATCH (c:Candidate {{name_kr: $name}})
                    MERGE (s:Skill {{name: $skill}})
                    MERGE (c)-[r:{action}]->(s)
                    """
                    session.run(query, name=name, skill=skill)
                    added_count += 1
                    
                print(f"[{completed}/{len(rows)}] {name} - ✅ {added_count}개 엣지 적재")

if __name__ == "__main__":
    process_deep_repair()
