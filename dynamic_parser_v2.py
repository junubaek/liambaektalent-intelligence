import os
import json
import time
import pdfplumber
import hashlib
import re
from docx import Document
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

FOLDER1 = r"C:\Users\cazam\Downloads\02_resume 전처리"
FOLDER2 = r"C:\Users\cazam\Downloads\02_resume_converted_docx"
FOLDER3 = r"C:\Users\cazam\Downloads\02_resume_converted_v8"
PROGRESS_FILE = r"C:\Users\cazam\Downloads\이력서자동분석검색시스템\processed.json"

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
    USED = "USED"

class ParsedEdge(BaseModel):
    action: ActionEnum
    skill: str
    
# Batch Action Edge Map for parsing multiple resumes cleanly
class CandidateEdges(BaseModel):
    candidate_name: str = Field(description="제공된 텍스트의 [후보자명: OOO] 에서 OOO 부분과 글자 하나 다르지 않게 동일해야 함")
    edges: list[ParsedEdge]

class BatchActionEdgeMap(BaseModel):
    results: list[CandidateEdges]

# ── 공통 지시어 ────────────────────────────────────
SYSTEM_INSTRUCTION = """
이력서 텍스트에서 후보자가 실제로 수행한 행위를 추출합니다.
각 후보자별로 결과를 추출할 때, `candidate_name` 필드는 파싱용으로 제공된 [후보자명: OOO] 형태의 헤더에서 OOO 부분을 절대 변경하지 말고 100% 동일한 글자로 복사해야 합니다. (이름이 불일치하면 시스템 에러가 발생하여 저장되지 않습니다.)

- action: 반드시 한정된 9개 동사 Enum 내에서만 선택하세요.
  * BUILT: 직접 코드 작성 또는 시스템/인프라 구축
  * DESIGNED: 아키텍처, 정책, UX, BM 등 기획/설계
  * MANAGED: 기존 시스템, 조직, 프로세스 운영/관리
  * ANALYZED: 데이터 추출/분석하여 인사이트 도출
  * LAUNCHED: 프로덕트/서비스를 책임지고 시장에 출시
  * NEGOTIATED: 외부와 협상/영업하거나 계약 체결
  * GREW: 매출, 트래픽, 유저 수 등 지표를 수치적으로 성장
  * SUPPORTED: 주도적 역할 아님, 협업/일부 지원
  * USED: 특정 도구나 인프라를 기반(기반 환경)으로 사용함

[1우선순위: 고유명사 원형 보존 원칙 (최우선 최우선!)]
프레임워크, 라이브러리, 툴, 플랫폼 이름(OpenStack, Terraform, Kubernetes, vLLM, PyTorch, LangGraph, CUDA, RDMA 등)은 절대 상위 개념으로 요약하지 말고, 이력서에 적힌 영문 원형 그대로 독립된 노드로 추출해라. 
목록(2순위)에 없는 단어라도 영문 고유명사면 아래 수식어 패턴을 포함해 무조건 원형 그대로 추출할 것.
- built on X → (후보자) USED X
- using X → (후보자) USED X  
- based on X → (후보자) USED X
- powered by X → (후보자) USED X
- leveraged X → (후보자) BUILT X
예시:
'MySQL service built on in-house OpenStack'
→ (후보자) -[:USED]-> (OpenStack)

[2순위: 그 외 일반 스킬은 아래 목록 기준으로 정규화]
(단, 위 1순위에 해당하는 영문 고유명사는 이 2순위 목록 제한을 무시하고 추출할 것)
Payment_and_Settlement_System, Product_Service_Planning, Business_Model_Planning, Platform_Operations_Planning, Product_Manager,
Data_Pipeline_Construction, Data_Engineering, Data_Analysis,
Backend, Frontend, Machine_Learning, MLOps, DevOps,
Financial_Accounting, Corporate_Strategic_Planning, 사업개발_BD, 퍼포먼스마케팅,
Treasury_Management, FX_Dealing, Corporate_Funding, IPO_Preparation_and_Execution,
Recruiting_and_Talent_Acquisition, Organizational_Development, B2B영업, 물류_Logistics,
Backend_Python, Backend_Java, Backend_Go, Backend_Node,
Kubernetes, Infrastructure_and_Cloud, 보안_Security, FinTech,
Natural_Language_Processing, 컴퓨터비전_CV, 추천시스템, Deep_Learning,
Corporate_Legal_Counsel, Intellectual_Property, Legal_Compliance, Contract_Management, Litigation

한 스킬에 여러 행동이 보이면 복수 동사 Multi-Edge 모두 생성해라.
스킬 노드는 검색 가능한 기술 명사여야 한다.
다음은 스킬 노드로 추출하면 안 됨:
- 숫자+단위 조합 (예: 32bit/64bit Architecture)
- 특수문자 포함 수치 표현 (예: L2/L3 Network)
- 회사명, 프로젝트명, 서비스명
- 단순 형용사/부사 (예: High Performance)

올바른 예시:
RTOS, FPGA, Linux_Kernel, NPU, 
vLLM, Kubernetes, Terraform, RDMA,
Memory_Profiling, Board_Bringup, 
On_Device_Compile

[문장 분석 Few-Shot 예시]
1. "신규 결제 서비스를 시장에 출시했습니다" -> action: "LAUNCHED", skill: "Payment_and_Settlement_System"
2. "주요 파트너사와 물류 제휴 계약을 협상했습니다" -> action: "NEGOTIATED", skill: "물류_Logistics"
3. "추천시스템 모델을 고도화하여 MAU를 6개월 만에 3배 성장시켰습니다" -> action: "GREW", skill: "추천시스템"
4. "앱 화면 UX와 어드민 시스템을 전담하여 설계했습니다" -> action: "DESIGNED", skill: "Product_Service_Planning"
"""

DUMMY_PADDING = "\n# " + ("PADDING " * 1500)
SYSTEM_INSTRUCTION += DUMMY_PADDING

cached_content_name = None
cache_created_at = 0

def refresh_cache_if_needed():
    global cache_created_at, cached_content_name
    if not cached_content_name:
        try:
            print("[Info] Context Caching 시스템 지시서 캐싱 시도 중...")
            from google.genai import types
            cache = client.caches.create(
                model=MODEL_ID,
                config=types.CreateCachedContentConfig(
                    system_instruction=SYSTEM_INSTRUCTION,
                    contents=[types.Content(role="user", parts=[types.Part.from_text(text="시스템 프롬프트 캐싱용 초기화 구문입니다.")])],
                    ttl="3600s",
                )
            )
            cached_content_name = cache.name
            cache_created_at = time.time()
            print(f"[Info] 캐시 생성 성공! 이름: {cached_content_name}")
        except Exception as e:
            print(f"[Info] 캐싱 모드 실패. 일반 파싱 진행. {e}")
            
    if cached_content_name and time.time() - cache_created_at > (45 * 60):
        try:
            print("[Info] 45분 경과: 캐시 TTL을 연장합니다.")
            client.caches.update(name=cached_content_name, ttl="3600s")
            cache_created_at = time.time()
            print("[Info] 캐시 TTL 연장 성공")
        except Exception as e:
            print(f"[Warning] 캐시 연장 실패. 폴백 활성화: {e}")
            cached_content_name = None

def extract_text(filepath):
    ext = filepath.rsplit(".", 1)[-1].lower()
    try:
        if ext == "pdf":
            with pdfplumber.open(filepath) as pdf:
                return "\n".join(p.extract_text() or "" for p in pdf.pages)
        elif ext in ("docx", "doc"):
            doc = Document(filepath)
            return "\n".join(p.text for p in doc.paragraphs)
    except:
        pass
    return ""

def calculate_cost(usage):
    in_t = getattr(usage, "prompt_token_count", 0) or 0
    out_t = getattr(usage, "candidates_token_count", 0) or 0
    c_t = getattr(usage, "cached_content_token_count", 0) or 0
    cost_usd = ((in_t - c_t) * 0.000000075) + (c_t * 0.00000001875) + (out_t * 0.00000030)
    return in_t, out_t, c_t, cost_usd * 1350

def parse_resume_batch(batch_dict):
    global cached_content_name
    if not batch_dict: return {}
    refresh_cache_if_needed()
    
    combined_body = "\n".join([f"======\n[후보자명: {name}]\n{text[:1500]}\n======" for name, text in batch_dict.items()])
    prompt = f"아래 여러 명의 이력서를 분석하세요.\n\n{combined_body}"
    
    config = types.GenerateContentConfig(
        response_mime_type="application/json",
        response_schema=BatchActionEdgeMap,
        system_instruction=SYSTEM_INSTRUCTION if not cached_content_name else None,
        cached_content=cached_content_name if cached_content_name else None
    )
    
    for attempt in range(3):
        try:
            res = client.models.generate_content(model=MODEL_ID, contents=prompt, config=config)
            in_t, out_t, c_t, krw = calculate_cost(res.usage_metadata)
            print(f" [Token Log] Input: {in_t}(Cached: {c_t}), Output: {out_t} | Cost: ₩{krw:.4f}")
            parsed_dict = {v.candidate_name: v.edges for v in res.parsed.results} if res.parsed else {}
            
            # ── Keyword Scan Booster ──────────────────
            # LLM이 놓친 고유명사 키워드를 raw_text에서 직접 스캔해서 USED 엣지로 보강
            SCAN_KEYWORDS = list(CANONICAL_MAP.keys())
            for name, expected_edges in parsed_dict.items():
                raw_text = batch_dict.get(name, "")
                if not raw_text: continue
                raw_lower = raw_text.lower()
                
                for keyword in SCAN_KEYWORDS:
                    # Ignore very short or generic keys to prevent noise, use word boundary
                    if len(keyword) < 2: continue
                    canonical = CANONICAL_MAP[keyword]
                    
                    pattern = r'\b' + re.escape(keyword.lower()) + r'\b'
                    if re.search(pattern, raw_lower):
                        # 이미 추출한 엣지에 없으면 추가
                        already_extracted = any(
                            getattr(e, 'skill', '') == canonical
                            for e in expected_edges
                        )
                        if not already_extracted:
                            expected_edges.append(ParsedEdge(action=ActionEnum.USED, skill=canonical))
            # ─────────────────────────────────────────
            
            return parsed_dict
        except Exception as e:
            if "429" in str(e) or "Quota" in str(e):
                time.sleep(10)
            elif "403" in str(e) or "not found" in str(e).lower():
                print(f"[Warning] 캐시가 서버에서 만료됨 '{cached_content_name}'. 캐시 없이 재시도합니다.")
                cached_content_name = None
                config.cached_content = None
                config.system_instruction = SYSTEM_INSTRUCTION
            else:
                print(f"Parsing error: {e}")
                return {}
    return {}

def extract_meta(filename_str):
    import re
    company = ""
    role = ""
    
    comp_match = re.search(r'\[(.*?)\]', filename_str)
    if comp_match: company = comp_match.group(1).strip()
        
    role_match = re.search(r'\((.*?)\)', filename_str)
    if role_match: role = role_match.group(1).strip()
        
    clean = re.sub(r'\[.*?\]|\(.*?\)|\..*', '', filename_str)
    clean = re.sub(r'부문|원본|최종|포트폴리오|이력서|합격|이력|Resume|CV', '', clean, flags=re.IGNORECASE)
    matches = re.findall(r'[가-힣]{2,4}', clean)
    stop_words = {'컨설팅','컨설턴트','경력','신입','기획','개발','채용','마케팅','디자인','운영','영업','전략','재무','회계','인사','총무','개발자','엔지니어','데이터','분석','사업','관리','팀장','리더','매니저','매니져','지원','담당','담당자','자산','운용'}
    valid = [m for m in matches if m not in stop_words]
    name_kr = valid[-1] if valid else (matches[-1] if matches else clean.strip())
    
    return company, role, name_kr

def extract_phone(text):
    match = re.search(r'010[- .]?\d{4}[- .]?\d{4}', text)
    return match.group(0) if match else ""

def extract_email(text):
    match = re.search(r'[\w.-]+@[\w.-]+\.\w+', text)
    return match.group(0) if match else ""

def log_to_update_candidates(name, kr, company):
    import json, os
    FILE = "update_candidates.json"
    data = []
    if os.path.exists(FILE):
        with open(FILE, "r", encoding="utf-8") as f:
            try: data = json.load(f)
            except: pass
    data.append({"name": name, "name_kr": kr, "company": company, "reason": "No contact, name collision"})
    with open(FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def log_unknown_skill(skill_name, candidate_name, raw_context):
    try:
        conn = sqlite3.connect("candidates.db")
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS unknown_skills (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                skill_name TEXT,
                candidate_name TEXT,
                detected_at DATETIME,
                raw_context TEXT
            )
        ''')
        cursor.execute('''
            INSERT INTO unknown_skills (skill_name, candidate_name, detected_at, raw_context)
            VALUES (?, ?, ?, ?)
        ''', (skill_name, candidate_name, datetime.now(), raw_context))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Failed to log unknown skill {skill_name}: {e}")

def get_existing_node_id(session, phone, email, name_kr, company):
    if phone:
        res = session.run("MATCH (c:Candidate {phone: $phone}) RETURN c.id as id", phone=phone)
        if res.peek(): return res.single()['id']
    if email:
        res = session.run("MATCH (c:Candidate {email: $email}) RETURN c.id as id", email=email)
        if res.peek(): return res.single()['id']
    if not phone and not email:
        res = session.run("MATCH (c:Candidate {name_kr: $name, company: $company}) RETURN c.id as id", name=name_kr, company=company)
        if res.peek(): return "MANUAL_REVIEW"
    return None

def save_edges(candidate_name, edges, raw_text):
    if not edges: return
    company, role, name_kr = extract_meta(candidate_name)
    phone = extract_phone(raw_text)
    email = extract_email(raw_text)
    document_hash = hashlib.sha256(raw_text.encode('utf-8')).hexdigest()
    
    embed_text = raw_text[:6000] if len(raw_text) > 6000 else raw_text
    vec = openai_client.embed_content(embed_text)
    
    with driver.session() as session:
        node_id = get_existing_node_id(session, phone, email, name_kr, company)
        if node_id == "MANUAL_REVIEW":
            log_to_update_candidates(candidate_name, name_kr, company)
            target_id = document_hash # 스킵하지 않고 새 해시로 생성
        else:
            target_id = node_id if node_id else document_hash
            session.run("MATCH (c:Candidate {id: $id})-[r]->() DELETE r", id=target_id)
            
        for edge_obj in edges:
            action = getattr(edge_obj, "action", "").upper()
            skill = getattr(edge_obj, "skill", "")
            if not action or not skill: continue
            
            if skill not in valid_nodes:
                log_unknown_skill(skill, candidate_name, raw_text)
                continue
            
            if vec:
                session.run(f"""
                    MERGE (c:Candidate {{id: $id}})
                    SET c.name = $name, 
                        c.name_kr = $name_kr, 
                        c.company = $company, 
                        c.role = $role,
                        c.phone = $phone,
                        c.email = $email,
                        c.embedding = $vec
                    MERGE (s:Skill {{name: $skill}})
                    MERGE (c)-[r:{action}]->(s)
                    SET r.source = 'llm_parsed_v2', r.confidence = 1.0
                """, 
                id=target_id, 
                name=candidate_name, 
                name_kr=name_kr, 
                company=company, 
                role=role, 
                phone=phone,
                email=email,
                skill=skill,
                vec=vec)
            else:
                session.run(f"""
                    MERGE (c:Candidate {{id: $id}})
                    SET c.name = $name, 
                        c.name_kr = $name_kr, 
                        c.company = $company, 
                        c.role = $role,
                        c.phone = $phone,
                        c.email = $email
                    MERGE (s:Skill {{name: $skill}})
                    MERGE (c)-[r:{action}]->(s)
                    SET r.source = 'llm_parsed_v2', r.confidence = 1.0
                """, 
                id=target_id, 
                name=candidate_name, 
                name_kr=name_kr, 
                company=company, 
                role=role, 
                phone=phone,
                email=email,
                skill=skill)

def load_progress():
    if os.path.exists(PROGRESS_FILE):
        with open(PROGRESS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, list):
                return {name: {"text_hash": "", "name_kr": "", "phone": ""} for name in data}
            return data
    return {}

def save_progress(processed):
    with open(PROGRESS_FILE, "w", encoding="utf-8") as f:
        json.dump(processed, f, ensure_ascii=False, indent=2)

def collect_files():
    files = {}
    for folder in [FOLDER1, FOLDER2, FOLDER3]:
        if os.path.exists(folder):
            for f in os.listdir(folder):
                if f.endswith((".pdf", ".docx", ".doc")):
                    files[f.rsplit(".", 1)[0]] = os.path.join(folder, f)
    return files

def main():
    print("V2 Parser (Pydantic + 8 Verbs) Execution Started.")
    
    # 1. Flush entire Neo4j edges to prevent overlap (Commented out for resume)
    # print("[INIT] Deleting all candidate edges in Neo4j...")
    # with driver.session() as session:
    #     session.run("MATCH (c:Candidate)-[r]->(s:Skill) DELETE r")
        
    print("[INIT] Resuming parsing without flushing edges.")
    
    # 2. Load progress instead of resetting
    processed = load_progress()
    
    files = collect_files()
    all_names = list(files.keys())
        
    batch_size = 5
    
    for i in tqdm(range(0, len(all_names), batch_size)):
        batch_names = all_names[i:i+batch_size]
        batch_dict = {}
        for name in batch_names:
            if name not in processed:
                batch_dict[name] = extract_text(files[name])
                
        if not batch_dict: continue
        
        parsed_results = parse_resume_batch(batch_dict)
        for name, text in batch_dict.items():
            if name in parsed_results:
                edges = parsed_results.get(name, [])
                save_edges(name, edges, text)
                processed[name] = {"text_hash": hashlib.md5(text.encode('utf-8')).hexdigest()}
            
        save_progress(processed)

if __name__ == "__main__":
    main()
