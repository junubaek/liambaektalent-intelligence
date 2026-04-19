import os
import json
import time
import hashlib
import re
from neo4j import GraphDatabase
import sqlite3
from datetime import datetime
from ontology_graph import CANONICAL_MAP

valid_nodes = set(CANONICAL_MAP.values())

from google import genai
from google.genai import types
from pydantic import BaseModel, Field
from enum import Enum
from typing import List
from tqdm import tqdm
from connectors.openai_api import OpenAIClient

# ── 설정 ──────────────────────────────────────────
with open("secrets.json", "r", encoding="utf-8") as f:
    secrets = json.load(f)
GEMINI_API_KEY = secrets["GEMINI_API_KEY"]

PROGRESS_FILE = r"C:\Users\cazam\Downloads\이력서자동분석검색시스템\processed_step6.json"

NEO4J_URI = "neo4j://127.0.0.1:7687"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "toss1234"

client = genai.Client(api_key=GEMINI_API_KEY)
MODEL_ID = "gemini-2.5-flash"
openai_client = OpenAIClient(secrets.get("OPENAI_API_KEY", ""))
driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))

# ── 스키마 정의 ────────────────────────────────────
class ActionEnum(str, Enum):
    BUILT = "BUILT"
    DESIGNED = "DESIGNED"
    MANAGED = "MANAGED"
    ANALYZED = "ANALYZED"
    LAUNCHED = "LAUNCHED"
    NEGOTIATED = "NEGOTIATED"
    GREW = "GREW"
    SUPPORTED = "SUPPORTED"
    MIGRATED = "MIGRATED"
    DEPLOYED = "DEPLOYED"
    RESOLVED = "RESOLVED"
    CLOSED = "CLOSED"
    DRAFTED = "DRAFTED"

class ParsedEdge(BaseModel):
    action: ActionEnum
    skill: str
    
class CandidateEdges(BaseModel):
    candidate_name: str = Field(description="제공된 텍스트의 [후보자명: OOO] 에서 OOO 부분과 글자 하나 다르지 않게 동일해야 함")
    edges: list[ParsedEdge]

class BatchActionEdgeMap(BaseModel):
    results: list[CandidateEdges]

# ── 공통 지시어 (Phase 3 적용본) ─────────────────────
SYSTEM_INSTRUCTION = """
이력서 텍스트에서 후보자가 실제로 수행한 행위를 추출합니다.
각 후보자별로 결과를 추출할 때, `candidate_name` 필드는 파싱용으로 제공된 [후보자명: OOO] 형태의 헤더에서 OOO 부분을 절대 변경하지 말고 100% 동일한 글자로 복사해야 합니다.

- action: 반드시 한정된 8개 동사 Enum 내에서만 선택하세요.
  * BUILT: 직접 코드 작성 또는 시스템/인프라 구축
  * DESIGNED: 아키텍처, 정책, UX, BM 등 기획/설계
  * MANAGED: 기존 시스템, 조직, 프로세스 운영/관리
  * ANALYZED: 데이터 추출/분석하여 인사이트 도출
  * LAUNCHED: 프로덕트/서비스를 책임지고 시장에 출시
  * NEGOTIATED: 외부와 협상/영업하거나 계약 체결
  * GREW: 매출, 트래픽, 유저 수 등 지표를 수치적으로 성장
  * SUPPORTED: 주도적 역할 아님, 협업/일부 지원

- skill: 반드시 아래 목록 내에서만 선택 (Category Node 및 대표 Canonical 포함):
Payment_and_Settlement_System, Product_Service_Planning, Business_Model_Planning, Platform_Operations_Planning, Product_Manager,
Data_Pipeline_Construction, Data_Engineering, Data_Analysis,
Backend, Frontend, Machine_Learning, MLOps, DevOps,
Financial_Accounting, Corporate_Strategic_Planning, 사업개발_BD, 퍼포먼스마케팅,
Treasury_Management, FX_Dealing, Corporate_Funding, IPO_Preparation_and_Execution,
Recruiting_and_Talent_Acquisition, Organizational_Development, B2B영업, SCM,
Backend_Python, Backend_Java, Backend_Go, Backend_Node,
Kubernetes, Infrastructure_and_Cloud, 정보보안_Information_Security, FinTech,
Natural_Language_Processing, 컴퓨터비전_CV, 추천시스템, Deep_Learning,
Corporate_Legal_Counsel, Intellectual_Property, Legal_Compliance, Contract_Management, Litigation

[고유명사 원형 보존 원칙]
프레임워크, 라이브러리, 툴, 플랫폼 이름(Kubernetes, Terraform, vLLM, PyTorch, LangGraph, CUDA, RDMA 등)은 절대 상위 개념(IaC, LLM_Engineering 등)으로 요약하거나 치환하지 마라.
이력서에 적힌 영문 원형 그대로 독립된 노드로 추출해라. 맵에 없는 단어라도 영문 고유명사면 원형 그대로.
한 스킬에 여러 행동이 보이면 복수 동사 Multi-Edge 모두 생성해라.
"""
DUMMY_PADDING = "\n# " + ("PADDING " * 1000)
SYSTEM_INSTRUCTION += DUMMY_PADDING

cached_content_name = None
cache_created_at = 0

def refresh_cache_if_needed():
    global cache_created_at, cached_content_name
    if not cached_content_name:
        try:
            from google.genai import types
            cache = client.caches.create(
                model=MODEL_ID,
                config=types.CreateCachedContentConfig(
                    system_instruction=SYSTEM_INSTRUCTION,
                    contents=[types.Content(role="user", parts=[types.Part.from_text(text="초기화")])],
                    ttl="3600s",
                )
            )
            cached_content_name = cache.name
            cache_created_at = time.time()
        except:
            pass
            
    if cached_content_name and time.time() - cache_created_at > 2700:
        try:
            client.caches.update(name=cached_content_name, ttl="3600s")
            cache_created_at = time.time()
        except:
            cached_content_name = None

def calculate_cost(usage):
    in_t = getattr(usage, "prompt_token_count", 0) or 0
    out_t = getattr(usage, "candidates_token_count", 0) or 0
    c_t = getattr(usage, "cached_content_token_count", 0) or 0
    cost_usd = ((in_t - c_t) * 0.000000075) + (c_t * 0.00000001875) + (out_t * 0.00000030)
    return cost_usd * 1350

def parse_resume_batch(batch_dict):
    global cached_content_name
    if not batch_dict: return {}
    refresh_cache_if_needed()
    
    combined_body = "\n".join([f"======\n[후보자명: {name}]\n{text[:2000]}\n======" for name, text in batch_dict.items()])
    prompt = f"아래 여러 명의 이력서를 분석하여 엣지를 추출하세요. 텍스트에서 명백히 확인되는 스킬 명사(고유명사)만 대상입니다.\n\n{combined_body}"
    
    config = types.GenerateContentConfig(
        response_mime_type="application/json",
        response_schema=BatchActionEdgeMap,
        system_instruction=SYSTEM_INSTRUCTION if not cached_content_name else None,
        cached_content=cached_content_name if cached_content_name else None
    )
    
    for attempt in range(3):
        try:
            res = client.models.generate_content(model=MODEL_ID, contents=prompt, config=config)
            return {v.candidate_name: v.edges for v in res.parsed.results} if res.parsed else {}
        except Exception as e:
            if "429" in str(e) or "Quota" in str(e):
                time.sleep(15)
            elif "403" in str(e) or "not found" in str(e).lower():
                cached_content_name = None
                config.cached_content = None
                config.system_instruction = SYSTEM_INSTRUCTION
            else:
                return {}
    return {}

def save_edges(cand_id, candidate_name, edges, raw_text, db_name_kr, db_company, db_phone, db_email):
    if not edges: return
    
    with driver.session() as session:
        session.run("MATCH (c:Candidate {id: $id})-[r]->() DELETE r", id=cand_id)
        
        for edge_obj in edges:
            action = getattr(edge_obj, "action", "").upper()
            skill = getattr(edge_obj, "skill", "")
            if not action or not skill: continue
            
            # Use valid_nodes mapping or keep raw noun
            if skill not in valid_nodes:
                mapped = CANONICAL_MAP.get(skill) or CANONICAL_MAP.get(skill.upper())
                if mapped: skill = mapped
                else:
                    if not re.search(r'[A-Za-z]', skill): continue 
            
            session.run(f"""
                MERGE (c:Candidate {{id: $id}})
                SET c.name = $name_kr, 
                    c.name_kr = $name_kr, 
                    c.company = $company, 
                    c.phone = $phone,
                    c.email = $email
                MERGE (s:Skill {{name: $skill}})
                MERGE (c)-[r:{action}]->(s)
                SET r.source = 'llm_parsed_step6', r.confidence = 1.0
            """, 
            id=cand_id, 
            name_kr=db_name_kr, 
            company=db_company, 
            phone=db_phone,
            email=db_email,
            skill=skill)

def load_progress():
    if os.path.exists(PROGRESS_FILE):
        with open(PROGRESS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_progress(processed):
    with open(PROGRESS_FILE, "w", encoding="utf-8") as f:
        json.dump(processed, f, ensure_ascii=False, indent=2)

def extract_company(careers_json):
    if not careers_json: return "미상"
    try:
        arr = json.loads(careers_json)
        if arr and isinstance(arr, list) and isinstance(arr[0], dict):
            return arr[0].get('company', '미상')
    except: pass
    return "미상"

def collect_candidates_from_db():
    conn = sqlite3.connect("candidates.db")
    c = conn.cursor()
    c.execute("SELECT id, name_kr, phone, email, careers_json, raw_text FROM candidates WHERE raw_text IS NOT NULL AND length(raw_text) > 100")
    rows = c.fetchall()
    conn.close()
    
    candidates = []
    for r in rows:
        c_id, name_kr, phone, email, careers_json, raw_text = r
        company = extract_company(careers_json)
        pseudo_filename = f"[{company}] {name_kr}"
        candidates.append({
            'id': c_id,
            'name_kr': name_kr,
            'company': company,
            'phone': phone,
            'email': email,
            'raw_text': raw_text,
            'pseudo_filename': pseudo_filename
        })
    return candidates

def main():
    print("Step 6: V8 Full Reparsing via SQLite Engine Started.", flush=True)
    
    processed = load_progress()
    candidates = collect_candidates_from_db()
    print(f"Total valid candidates from DB: {len(candidates)}", flush=True)
        
    batch_size = 5
    
    for i in tqdm(range(0, len(candidates), batch_size)):
        batch = candidates[i:i+batch_size]
        batch_dict = {}
        for c in batch:
            if str(c['id']) not in processed:
                batch_dict[c['pseudo_filename']] = c['raw_text']
                
        if not batch_dict: continue
        
        parsed_results = parse_resume_batch(batch_dict)
        for c in batch:
            c_name = c['pseudo_filename']
            if c_name in parsed_results:
                edges = parsed_results.get(c_name, [])
                save_edges(c['id'], c_name, edges, c['raw_text'], c['name_kr'], c['company'], c['phone'], c['email'])
                processed[str(c['id'])] = {"status": "done", "edge_count": len(edges)}
            
        save_progress(processed)
        time.sleep(1.0) # Rate limit safety

if __name__ == "__main__":
    main()
