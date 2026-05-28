import os
import sys
import json
import sqlite3
import time
import asyncio
from neo4j import GraphDatabase
from google import genai
from google.genai import types
from pydantic import BaseModel, Field
from enum import Enum
from typing import List
from tqdm import tqdm

sys.path.append(r'C:\Users\cazam\Downloads\이력서자동분석검색시스템')
from ontology_graph import CANONICAL_MAP

# Load secrets
with open("secrets.json", "r", encoding="utf-8") as f:
    secrets = json.load(f)

GEMINI_API_KEY = secrets["GEMINI_API_KEY"]
NEO4J_URI = secrets.get("NEO4J_URI", "neo4j://127.0.0.1:7687")
NEO4J_USER = secrets.get("NEO4J_USERNAME", "neo4j")
NEO4J_PASSWORD = secrets.get("NEO4J_PASSWORD", "toss1234")

client = genai.Client(api_key=GEMINI_API_KEY, http_options={'timeout': 60.0})
MODEL_ID = "gemini-2.5-flash"
driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))

# Define Pydantic Schema for Gemini Output
class ActionEnum(str, Enum):
    BUILT = "BUILT"
    DESIGNED = "DESIGNED"
    MANAGED = "MANAGED"
    ANALYZED = "ANALYZED"
    LED = "LED"
    LAUNCHED = "LAUNCHED"
    GREW = "GREW"
    NEGOTIATED = "NEGOTIATED"
    SUPPORTED = "SUPPORTED"

class SkillAction(BaseModel):
    skill: str = Field(description="Must match EXACTLY one of the 741 allowed standardized skills.")
    action: ActionEnum

class ChunkSkillMapping(BaseModel):
    company_name: str = Field(description="Must match the company name of the chunk.")
    skills_used: List[SkillAction]

class CandidateRefinementResult(BaseModel):
    candidate_id: str
    chunk_skills: List[ChunkSkillMapping]

class BatchRefinementMap(BaseModel):
    results: List[CandidateRefinementResult]

# Retrieve 741 standardized canonical skills
CANONICAL_SKILLS = sorted(list(set(CANONICAL_MAP.values())))
CANONICAL_SKILLS_STR = "\n".join([f"- {s}" for s in CANONICAL_SKILLS])

SYSTEM_PROMPT = f"""당신은 최고 기술 전문 헤드헌터이자 IT 아키텍처 역량 분석가입니다.
제공된 후보자의 비정형 이력서 텍스트와 현재 Neo4j에 생성되어 있는 경력 청크(Experience_Chunk) 리스트를 분석하여, 각 경력별로 사용된 표준 스킬 및 행동(Action Verb)을 정밀하게 추출해 온톨로지를 보강하는 것이 당신의 미션입니다.

[중요 규칙]
1. 아래 제공되는 '741개 표준 스킬 목록'에 속해 있는 스킬만 추출해야 합니다. 오타나 유사 단어는 절대 허용하지 않고 리스트 내 단어와 100% 철자 일치해야 합니다.
2. 각 스킬에 맞는 적절한 역할 동사(Action Verb)를 매핑하세요:
   - BUILT: 직접 개발, 구현, 엔지니어링 수행
   - DESIGNED: 아키텍처 설계, 설계 패턴 적용, 하드웨어 회로/RTL 설계
   - MANAGED: 인프라 관리, 팀 관리, 데이터베이스 운영
   - ANALYZED: 데이터 분석, 모델링 분석, 로그 모니터링 분석
   - LED: 프로젝트 리딩, 기술 리드
   - LAUNCHED: 서비스 출시, 비즈니스 런칭
   - GREW: 비즈니스 확장, 매출 성장
   - NEGOTIATED: 협상, 계약 조율
   - SUPPORTED: 유지보수, 고객 지원, 검증/테스트 보조

[741개 표준 스킬 목록]
{CANONICAL_SKILLS_STR}
"""

def parse_refinement_batch(batch_dict: dict, chunk_info_dict: dict) -> dict:
    prompt = "여기에 정밀 매핑을 보강할 후보자 이력서와 현재 경력 청크 목록이 있습니다:\n\n"
    for cid, text in batch_dict.items():
        if len(text) > 8000: text = text[:8000]
        chunks = chunk_info_dict.get(cid, [])
        prompt += f"--- START CANDIDATE [{cid}] ---\n"
        prompt += f"현재 존재하는 경력 청크 리스트:\n{json.dumps(chunks, ensure_ascii=False, indent=2)}\n\n"
        prompt += f"이력서 원문:\n{text}\n"
        prompt += f"--- END CANDIDATE [{cid}] ---\n\n"
        
    config = types.GenerateContentConfig(
        response_mime_type="application/json",
        response_schema=BatchRefinementMap,
        system_instruction=SYSTEM_PROMPT,
        temperature=0.1
    )
    
    for attempt in range(3):
        try:
            response = client.models.generate_content(model=MODEL_ID, contents=prompt, config=config)
            parsed = response.parsed
            if parsed and parsed.results:
                return {item.candidate_id: item.chunk_skills for item in parsed.results}
        except Exception as e:
            print(f"Gemini API Error (Attempt {attempt+1}/3): {e}")
            if attempt < 2:
                time.sleep(5)
            else:
                print("All attempts failed for this batch.")
    return {}

def process_candidate_refinement(cid, chunk_skills, chunk_map):
    with driver.session() as session:
        valid_skills = set(CANONICAL_SKILLS)
        
        for cs in chunk_skills:
            comp_name = cs.company_name
            # Fuzzy match to match chunk_id
            chunk_id = None
            for orig_comp, cid_val in chunk_map.items():
                if comp_name.lower().replace(" ", "") in orig_comp.lower().replace(" ", "") or \
                   orig_comp.lower().replace(" ", "") in comp_name.lower().replace(" ", ""):
                    chunk_id = cid_val
                    break
            
            if not chunk_id:
                # If no matching chunk, find any chunk or skip
                continue
                
            for sa in cs.skills_used:
                skill = sa.skill.strip()
                if skill not in valid_skills:
                    # Try fallback to canonical mapping if not 100% matched
                    skill_norm = skill.lower().replace('_', ' ').strip()
                    if skill in CANONICAL_MAP:
                        skill = CANONICAL_MAP[skill]
                    elif skill_norm in CANONICAL_MAP:
                        skill = CANONICAL_MAP[skill_norm]
                    else:
                        continue
                        
                action = sa.action.value.upper()
                session.run(f"""
                    MATCH (e:Experience_Chunk {{id: $chunk_id}})
                    MERGE (s:Skill {{name: $skill}})
                    MERGE (e)-[r:{action}]->(s)
                    SET r.source = 'precision_refinement_v11', r.confidence = 1.0
                """, chunk_id=chunk_id, skill=skill)

BATCH_SIZE = 10
PROCESSED_FILE = "processed_refinement.json"

def load_processed():
    if os.path.exists(PROCESSED_FILE):
        with open(PROCESSED_FILE, 'r') as f:
            return set(json.load(f))
    return set()

def save_processed(processed_set):
    with open(PROCESSED_FILE, 'w') as f:
        json.dump(list(processed_set), f)

def main():
    print("V11 LLM Multi-step Precision Refinement Started")
    
    with open('refinement_targets.json', 'r', encoding='utf-8') as f:
        targets = json.load(f)
        
    target_ids = [t['id'] for t in targets]
    processed_ids = load_processed()
    remaining_targets = [tid for tid in target_ids if tid not in processed_ids]
    
    print(f"Total targets: {len(target_ids)}")
    print(f"Already processed: {len(processed_ids)}")
    print(f"Remaining targets: {len(remaining_targets)}")
    
    conn = sqlite3.connect('candidates.db')
    cur = conn.cursor()
    
    for i in tqdm(range(0, len(remaining_targets), BATCH_SIZE)):
        batch_ids = remaining_targets[i:i+BATCH_SIZE]
        
        # 1. Fetch chunks info from Neo4j to give context to Gemini
        chunk_info_dict = {}
        chunk_map_dict = {} # Mapping company_name to chunk_id
        
        with driver.session() as session:
            for cid in batch_ids:
                chunks_res = session.run("""
                    MATCH (c:Candidate {id: $cid})-[:HAS_EXPERIENCE]->(e:Experience_Chunk)
                    RETURN e.id as id, e.company_name as comp, e.role_name as role, e.description as desc
                """, cid=cid).data()
                
                chunk_info_dict[cid] = [
                    {"company_name": r['comp'], "role_name": r['role'], "description": r['desc']}
                    for r in chunks_res
                ]
                chunk_map_dict[cid] = {r['comp']: r['id'] for r in chunks_res}
        
        # 2. Get raw_text from SQLite
        placeholders = ','.join(['?'] * len(batch_ids))
        cur.execute(f"SELECT id, raw_text FROM candidates WHERE id IN ({placeholders})", batch_ids)
        rows = cur.fetchall()
        batch_dict = {row[0]: row[1] for row in rows if row[1]}
        
        if not batch_dict:
            for tid in batch_ids: processed_ids.add(tid)
            save_processed(processed_ids)
            continue
            
        # 3. Call Gemini
        parsed_results = parse_refinement_batch(batch_dict, chunk_info_dict)
        
        # 4. Save and MERGE edges
        for cid in batch_ids:
            if cid in parsed_results:
                process_candidate_refinement(cid, parsed_results[cid], chunk_map_dict.get(cid, {}))
            processed_ids.add(cid)
            
        save_processed(processed_ids)
        time.sleep(1)
        
    conn.close()
    driver.close()
    print("\n--- V11 Precision Refinement Complete ---")

if __name__ == "__main__":
    main()
