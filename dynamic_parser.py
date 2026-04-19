import os
import json
import time
import pdfplumber
import google.generativeai as genai
from docx import Document
from neo4j import GraphDatabase
from tqdm import tqdm

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

# ── Gemini 설정 ────────────────────────────────────
genai.configure(api_key=GEMINI_API_KEY)
# Since the api key might hit limits, we add a simple fallback block if needed later.
model = genai.GenerativeModel("gemini-2.5-flash")

# ── Neo4j 연결 ─────────────────────────────────────
driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))

# ── 텍스트 추출 ────────────────────────────────────
def extract_text(filepath):
    ext = filepath.rsplit(".", 1)[-1].lower()
    try:
        if ext == "pdf":
            with pdfplumber.open(filepath) as pdf:
                return "\n".join(p.extract_text() or "" for p in pdf.pages)
        elif ext in ("docx", "doc"):
            doc = Document(filepath)
            return "\n".join(p.text for p in doc.paragraphs)
    except Exception as e:
        print(f"Extraction error for {filepath}: {e}")
        return ""
    return ""

# ── Gemini 파싱 ────────────────────────────────────
def parse_resume(text):
    if not text or len(text) < 100:
        return []
    
    prompt = f"""
이력서 텍스트에서 후보자가 실제로 수행한 행위를 추출해줘.
반드시 아래 JSON 배열 형식으로만 응답해. 다른 텍스트 없이.

형식:
[
  {{"action": "BUILT", "skill": "Payment_and_Settlement_System", "confidence": 0.95, "evidence_span": "정산 시스템 아키텍처를 직접 설계했습니다"}},
  {{"action": "DESIGNED", "skill": "Data_Pipeline_Construction", "confidence": 0.72, "evidence_span": "관련 업무에 일부 참여했습니다"}}
]

각 항목에 다음 값을 포함해:
- action: 반드시 아래 8개 동사 중 하나만 선택 (다른 단어 절대 금지, 예: ANALYZE 식의 변형 불가)
  * BUILT: 직접 코드 작성 또는 시스템/인프라 구축
  * DESIGNED: 아키텍처, 정책, UX, BM 등 기획/설계
  * MANAGED: 기존 시스템, 조직, 프로세스 운영/관리
  * ANALYZED: 데이터 추출/분석하여 인사이트 도출
  * LAUNCHED: 프로덕트/서비스를 책임지고 시장에 출시
  * NEGOTIATED: 외부와 협상/영업하거나 계약 체결
  * GREW: 매출, 트래픽, 유저 수 등 지표를 수치적으로 성장
  * SUPPORTED: 주도적 역할 아님, 협업/일부 지원
- skill: 기본적으로 아래 목록에서 선택하되, 하단 
[고유명사 원형 보존 원칙]
프레임워크, 라이브러리, 툴, 플랫폼 이름(Kubernetes, Terraform, vLLM, PyTorch, LangGraph, CUDA, RDMA 등)은 절대 상위 개념(IaC, LLM_Engineering 등)으로 요약하거나 치환하지 마라.
이력서에 적힌 영문 원형 그대로 독립된 노드로 추출해라. 맵에 없는 단어라도 영문 고유명사면 원형 그대로.
한 스킬에 여러 행동이 보이면 복수 동사 Multi-Edge 모두 생성해라.

[특별 추출 카테고리]에 해당하는 구체적인 기술/전문 용어가 원문에 명시되어 있다면 목록에 없더라도 해당 단어 자체를 추출해. 단, 대학명, 회사명, 학회명(예: ACL, EMNLP)은 스킬이 아니므로 추출 금지.
- confidence: 이 매핑에 대해 얼마나 확신하는지 0.0 ~ 1.0 사이의 숫자
- evidence_span: 이 판단을 내리게 한 이력서 원문의 정확한 문구


[고유명사 원형 보존 원칙]
프레임워크, 라이브러리, 툴, 플랫폼 이름(Kubernetes, Terraform, vLLM, PyTorch, LangGraph, CUDA, RDMA 등)은 절대 상위 개념(IaC, LLM_Engineering 등)으로 요약하거나 치환하지 마라.
이력서에 적힌 영문 원형 그대로 독립된 노드로 추출해라. 맵에 없는 단어라도 영문 고유명사면 원형 그대로.
한 스킬에 여러 행동이 보이면 복수 동사 Multi-Edge 모두 생성해라.

[특별 추출 카테고리]
- AI/ML 프레임워크: vLLM, SGLang, TensorRT-LLM, llama.cpp, Triton, JAX 등
- GPU/NPU: CUDA, NPU, Tensix, RISC-V_Vector 등
- 네트워크: InfiniBand, NCCL, RDMA, OpenMPI, DPDK, RoCE 등
- 반도체/HW: PCIe, NVMe, CXL, SoC, AUTOSAR 등
- 프로그래밍: Rust, Go, Assembly 등
- 재무/회계/비즈: K-IFRS, US GAAP, IFRS, 연결회계, 내부통제, CDD, CPA, AICPA, CFA, Due Diligence, Valuation 등
- LLM/AI 연구: LLM-as-a-Judge, Knowledge_Distillation, RLHF, Chain_of_Thought 등


skill은 아래 목록 중에서만 선택:
Payment_and_Settlement_System, Service_Planning, Product_Manager,
Data_Pipeline_Construction, Data_Engineering, Data_Analysis,
Backend, Frontend, Machine_Learning, MLOps, DevOps,
Financial_Accounting, Corporate_Strategic_Planning, 사업개발_BD, 퍼포먼스마케팅,
Treasury_Management, FX_Dealing, Corporate_Funding, IPO_Preparation_and_Execution,
Recruiting_and_Talent_Acquisition, Organizational_Development, B2B영업, 물류_Logistics,
Backend_Python, Backend_Java, Backend_Go, Backend_Node,
Kubernetes, Infrastructure_and_Cloud, 보안_Security, FinTech,
Natural_Language_Processing, 컴퓨터비전_CV, 추천시스템, Deep_Learning,
Corporate_Legal_Counsel, Intellectual_Property, Legal_Compliance, Contract_Management, Litigation

이력서:
{text[:3000]}
"""
    import time
    import json
    for attempt in range(3):
        try:
            response = model.generate_content(prompt)
            raw = response.text.strip()
            raw = raw.replace("```json", "").replace("```", "").strip()
            return json.loads(raw)
        except Exception as e:
            err_str = str(e)
            if "429" in err_str or "Quota" in err_str or "exhausted" in err_str.lower():
                time.sleep(10)
            else:
                break
    return []

def parse_resume_batch(batch_dict):
    """
    batch_dict: dict of {name: text} (up to 5 items)
    Returns: dict of {name: edges_list}
    """
    import json, time
    if not batch_dict: return {}
    
    # 텍스트 길이 제한 (각 1500자)
    combined_texts = []
    for name, text in batch_dict.items():
        combined_texts.append(f"======\n[후보자명: {name}]\n{text[:1500]}\n======")
        
    combined_body = "\n".join(combined_texts)
    
    prompt = f"""
아래 여러 명의 이력서를 분석하여 각각 수행한 행위를 추출해.
반드시 아래 JSON Object 형식으로만 응답해. 키값은 대괄호 안의 후보자명과 정확히 일치해야 해.

형식:
{{
  "후보자A": [ {{"action": "BUILT", "skill": "Payment_and_Settlement_System", "confidence": 0.95, "evidence_span": "시스템 아키텍처를 직접 설계"}} ],
  "후보자B": [ {{"action": "DESIGNED", "skill": "Data_Pipeline_Construction", "confidence": 0.72, "evidence_span": "데이터 파이프라인 개발 보조"}} ]
}}

각 항목에 다음 값을 포함해:
- action: 반드시 아래 8개 동사 중 하나만 선택 (다른 단어 절대 금지, 예: ANALYZE 식의 변형 불가)
  * BUILT: 직접 코드 작성 또는 시스템/인프라 구축
  * DESIGNED: 아키텍처, 정책, UX, BM 등 기획/설계
  * MANAGED: 기존 시스템, 조직, 프로세스 운영/관리
  * ANALYZED: 데이터 추출/분석하여 인사이트 도출
  * LAUNCHED: 프로덕트/서비스를 책임지고 시장에 출시
  * NEGOTIATED: 외부와 협상/영업하거나 계약 체결
  * GREW: 매출, 트래픽, 유저 수 등 지표를 수치적으로 성장
  * SUPPORTED: 주도적 역할 아님, 협업/일부 지원
- skill: 기본적으로 아래 목록에서 선택하되, 하단 
[고유명사 원형 보존 원칙]
프레임워크, 라이브러리, 툴, 플랫폼 이름(Kubernetes, Terraform, vLLM, PyTorch, LangGraph, CUDA, RDMA 등)은 절대 상위 개념(IaC, LLM_Engineering 등)으로 요약하거나 치환하지 마라.
이력서에 적힌 영문 원형 그대로 독립된 노드로 추출해라. 맵에 없는 단어라도 영문 고유명사면 원형 그대로.
한 스킬에 여러 행동이 보이면 복수 동사 Multi-Edge 모두 생성해라.

[특별 추출 카테고리]에 해당하는 구체적인 기술/전문 용어가 원문에 명시되어 있다면 목록에 없더라도 해당 단어 자체를 추출해. 단, 대학명, 회사명, 학회명(예: ACL, EMNLP)은 스킬이 아니므로 추출 금지.
- confidence: 이 매핑에 대해 얼마나 확신하는지 0.0 ~ 1.0 사이의 숫자.
- evidence_span: 이 판단을 내리게 한 이력서 원문의 정확한 문구.


[고유명사 원형 보존 원칙]
프레임워크, 라이브러리, 툴, 플랫폼 이름(Kubernetes, Terraform, vLLM, PyTorch, LangGraph, CUDA, RDMA 등)은 절대 상위 개념(IaC, LLM_Engineering 등)으로 요약하거나 치환하지 마라.
이력서에 적힌 영문 원형 그대로 독립된 노드로 추출해라. 맵에 없는 단어라도 영문 고유명사면 원형 그대로.
한 스킬에 여러 행동이 보이면 복수 동사 Multi-Edge 모두 생성해라.

[특별 추출 카테고리]
- AI/ML 프레임워크: vLLM, SGLang, TensorRT-LLM, llama.cpp, Triton, JAX 등
- GPU/NPU: CUDA, NPU, Tensix, RISC-V_Vector 등
- 네트워크: InfiniBand, NCCL, RDMA, OpenMPI, DPDK, RoCE 등
- 반도체/HW: PCIe, NVMe, CXL, SoC, AUTOSAR 등
- 프로그래밍: Rust, Go, Assembly 등
- 재무/회계/비즈: K-IFRS, US GAAP, IFRS, 연결회계, 내부통제, CDD, CPA, AICPA, CFA, Due Diligence, Valuation 등
- LLM/AI 연구: LLM-as-a-Judge, Knowledge_Distillation, RLHF, Chain_of_Thought 등


skill 목록:
Payment_and_Settlement_System, Service_Planning, Product_Manager,
Data_Pipeline_Construction, Data_Engineering, Data_Analysis,
Backend, Frontend, Machine_Learning, MLOps, DevOps,
Financial_Accounting, Corporate_Strategic_Planning, 사업개발_BD, 퍼포먼스마케팅,
Treasury_Management, FX_Dealing, Corporate_Funding, IPO_Preparation_and_Execution,
Recruiting_and_Talent_Acquisition, Organizational_Development, B2B영업, 물류_Logistics,
Backend_Python, Backend_Java, Backend_Go, Backend_Node,
Kubernetes, Infrastructure_and_Cloud, 보안_Security, FinTech,
Natural_Language_Processing, 컴퓨터비전_CV, 추천시스템, Deep_Learning,
Corporate_Legal_Counsel, Intellectual_Property, Legal_Compliance, Contract_Management, Litigation

제시된 이력서들:
{combined_body}
"""
    for attempt in range(3):
        try:
            response = model.generate_content(prompt)
            raw = response.text.strip()
            raw = raw.replace("```json", "").replace("```", "").strip()
            parsed = json.loads(raw)
            return parsed
        except Exception as e:
            err_str = str(e)
            if "429" in err_str or "Quota" in err_str or "exhausted" in err_str.lower():
                time.sleep(10)
            else:
                break
    return {}

# ── Neo4j 저장 ─────────────────────────────────────
REVIEW_QUEUE_FILE = os.path.join(os.path.dirname(PROGRESS_FILE), "review_queue.json")

def save_edges(candidate_name, edges, filepath=None):
    if not edges:
        return
        
    review_list = []
    
    with driver.session() as session:
        # 새 엣지를 덮어쓰기 위해 기존 엣지 전체 삭제 (단절 방지용 업데이트 방식)
        session.run("MATCH (c:Candidate)-[r]->() WHERE c.name = $name OR c.name_kr = $name DELETE r", name=candidate_name)
        
        for edge in edges:
            action = edge.get("action", "").upper()
            skill = edge.get("skill", "")
            try:
                confidence = float(edge.get("confidence", 1.0))
            except:
                confidence = 0.5
            evidence_span = edge.get("evidence_span", "")
            
            if not action or not skill:
                continue
                
            if confidence >= 0.85:
                session.run(f"""
                    MERGE (c:Candidate {{name: $name}})
                    MERGE (s:Skill {{name: $skill}})
                    MERGE (c)-[r:{action}]->(s)
                    SET r.source = 'llm_parsed', r.confidence = $confidence, r.evidence_span = $evidence_span
                """, name=candidate_name, skill=skill, confidence=confidence, evidence_span=evidence_span)
            elif confidence >= 0.6:
                filename = os.path.basename(filepath) if filepath else f"{candidate_name}.pdf"
                review_list.append({
                    "candidate": candidate_name,
                    "action": action,
                    "skill": skill,
                    "confidence": confidence,
                    "evidence_span": evidence_span,
                    "file": filename
                })
            else:
                print(f"[Skip] 신뢰도 미달 ({confidence}): {candidate_name} - {action} - {skill} | 근거: {evidence_span}")

    if review_list:
        try:
            if os.path.exists(REVIEW_QUEUE_FILE):
                with open(REVIEW_QUEUE_FILE, "r", encoding="utf-8") as f:
                    existing = json.load(f)
            else:
                existing = []
        except Exception:
            existing = []
            
        existing.extend(review_list)
        with open(REVIEW_QUEUE_FILE, "w", encoding="utf-8") as f:
            json.dump(existing, f, ensure_ascii=False, indent=2)


# ── 진행상황 관리 및 중복 감지 ──────────────────────────────────
import hashlib
import re

phone_pattern = re.compile(r"010-\d{4}-\d{4}")
kr_name_pattern = re.compile(r"[가-힣]+")

def get_name_kr(raw_name):
    # Extract only Korean characters from filename
    matches = kr_name_pattern.findall(raw_name)
    return "".join(matches) if matches else ""

def detect_duplicates(name, text, processed):
    text_hash = hashlib.md5(text.encode('utf-8')).hexdigest()
    
    # 1. Check Hash collision
    for v in processed.values():
        val_hash = v.get("text_hash", "")
        if val_hash and val_hash == text_hash:
            return "HASH_DUPE", {"text_hash": text_hash, "name_kr": "", "phone": ""}
            
    # 2. Check Name + Phone collision
    name_kr = get_name_kr(name)
    phones = phone_pattern.findall(text)
    phone = phones[0] if phones else ""
    
    meta_data = {"text_hash": text_hash, "name_kr": name_kr, "phone": phone}
    
    if phone and name_kr:
        for v in processed.values():
            if v.get("phone") == phone and v.get("name_kr") == name_kr:
                return "UPDATE_DUPE", meta_data
                
    return "OK", meta_data

def load_progress():
    import json, os
    if os.path.exists(PROGRESS_FILE):
        with open(PROGRESS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, list):
                # Migration
                migrated = {name: {"text_hash": "", "name_kr": "", "phone": ""} for name in data}
                return migrated
            return data
    return {}

def save_progress(processed):
    import json
    with open(PROGRESS_FILE, "w", encoding="utf-8") as f:
        json.dump(processed, f, ensure_ascii=False, indent=2)

# ── 파일 목록 수집 ─────────────────────────────────
def collect_files():
    import os
    files = {}
    if os.path.exists(FOLDER1):
        for f in os.listdir(FOLDER1):
            name = f.rsplit(".", 1)[0]
            files[name] = os.path.join(FOLDER1, f)
    if os.path.exists(FOLDER2):
        for f in os.listdir(FOLDER2):
            name = f.rsplit(".", 1)[0]
            files[name] = os.path.join(FOLDER2, f)
    if os.path.exists(FOLDER3):
        for f in os.listdir(FOLDER3):
            name = f.rsplit(".", 1)[0]
            files[name] = os.path.join(FOLDER3, f)
    return files

# ── 메인 실행 ──────────────────────────────────────
def main():
    import time
    import json
    import os
    
    UPDATE_CANDIDATES_FILE = "update_candidates.json"
    files = collect_files()
    processed = load_progress()
    
    # Restrict to preflight unique names to save API calls
    allowed_names = set()
    allowed_names = None
    """
    try:
        if os.path.exists("preflight_unique.json"):
            with open("preflight_unique.json", "r", encoding="utf-8") as f:
                allowed_names = set(json.load(f))
            print(f"[Info] Loaded {len(allowed_names)} strict targets from preflight_unique.json")
    except Exception as e:
        print("[Warning] Could not load preflight list, processing all remaining.")
    """
        
    remaining = {}
    for k, v in files.items():
        if k not in processed:
            if allowed_names and k not in allowed_names:
                continue
            remaining[k] = v
    
    remaining = {k: v for k, v in remaining.items() if str(v).lower().endswith('.pdf') or str(v).lower().endswith('.docx')}
    
    print(f"전체: {len(files)}개 / 완료: {len(processed)}개 / 대상: {len(remaining)}개")
    
    # Batch Processing Logic
    remaining_items = list(remaining.items())
    batch_size = 5
    
    for i in tqdm(range(0, len(remaining_items), batch_size)):
        chunk = remaining_items[i : i+batch_size]
        batch_dict = {}
        batch_meta = {}
        batch_filepath = {}
        
        for name, filepath in chunk:
            text = extract_text(filepath)
            if len(text) >= 100:
                reason, meta = detect_duplicates(name, text, processed)
                if reason == "HASH_DUPE":
                    print(f"\n[해시 중복 감지] {name} - 스킵됨")
                    processed[name] = meta
                    continue
                elif reason == "UPDATE_DUPE":
                    print(f"\n[업데이트 이력서 감지] {name} - 수동 확인 필요")
                    try:
                        if os.path.exists(UPDATE_CANDIDATES_FILE):
                            with open(UPDATE_CANDIDATES_FILE, "r", encoding="utf-8") as f:
                                up_list = json.load(f)
                        else:
                            up_list = []
                    except Exception:
                        up_list = []
                    up_list.append(name)
                    with open(UPDATE_CANDIDATES_FILE, "w", encoding="utf-8") as f:
                        json.dump(up_list, f, ensure_ascii=False, indent=2)
                    continue
                
                batch_dict[name] = text
                batch_meta[name] = meta
                batch_filepath[name] = filepath
            else:
                processed[name] = {"text_hash": "", "name_kr": "", "phone": ""}  # skip empty
        
        if not batch_dict:
            if len(processed) % 10 < batch_size:
                save_progress(processed)
            continue
            
        print(f"\n[Batch Parsing] {list(batch_dict.keys())}")
        batch_results = parse_resume_batch(batch_dict)
        
        # Fallback Check
        for name in batch_dict.keys():
            if name in batch_results:
                edges = batch_results[name]
                save_edges(name, edges, batch_filepath.get(name))
                processed[name] = batch_meta.get(name, {})
            else:
                # LLM Omission Fallback
                print(f"\n[Fallback] {name} 누락 감지. 개별 처리 재시도...")
                edges = parse_resume(batch_dict[name])
                save_edges(name, edges, batch_filepath.get(name))
                processed[name] = batch_meta.get(name, {})
                
        if len(processed) % 10 < batch_size:  # Approximate save step
            save_progress(processed)
            
        time.sleep(1)
        
    save_progress(processed)
    print("완료!")

if __name__ == "__main__":
    main()
