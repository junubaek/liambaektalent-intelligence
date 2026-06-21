import sqlite3
import json
import time
import sys
from neo4j import GraphDatabase
import google.generativeai as genai

sys.stdout.reconfigure(encoding='utf-8')

# 1. Load secrets
with open('secrets.json', 'r', encoding='utf-8') as f:
    secrets = json.load(f)

# Configure Gemini
genai.configure(api_key=secrets["GEMINI_API_KEY"])
model = genai.GenerativeModel("gemini-2.5-flash")

# Neo4j connection
driver = GraphDatabase.driver(
    secrets['NEO4J_URI'],
    auth=(secrets['NEO4J_USERNAME'], secrets['NEO4J_PASSWORD'])
)

from ontology_graph import CANONICAL_MAP

def normalize_skill(skill_name: str) -> str:
    if skill_name in CANONICAL_MAP:
        return CANONICAL_MAP[skill_name]
    lower = skill_name.lower()
    for key, val in CANONICAL_MAP.items():
        if key.lower() == lower:
            return val
    return skill_name

# Target candidates to re-parse using Gemini
targets = [
    ('한경환', '1aaad2d3-348d-48f7-8501-38d7c1f7df03'),
    ('김태경', 'fbc27466-7587-45e6-b459-c2920b5d71fe'),
    ('김일곤', 'e88ea471-e1eb-4c40-b5e1-7648e340fac4'),
    ('유정한', '31f22567-1b6f-8152-93ca-ca5ab3080016'),
    ('김형수', '4b4c3372-401b-4897-a9b3-d36a3ba3de37'),
    ('오수영', '32e22567-1b6f-8181-9992-d986271e941f'),
    ('배정현', 'fafa2636-cf0b-42c1-8c18-598d089e9c61'),
    ('하현재', 'ba4abc09-302e-4fd4-ae93-b8af52aed567'),
    ('김진영', '32022567-1b6f-819f-b62e-fa5ecb02e3de'),
    ('김진호', '1c3e3279-b0c5-4661-9dcf-7fa929dd47bb'),
    ('박천혁', '3d322d13-0699-4453-b70e-5a4c2aac38f9'),
]

# We expand [Skill 목록] to include the new custom skills we added to the ontology
MEGA_PROMPT = """이력서 텍스트를 분석해서 아래 구조를 JSON Object 형식으로 출력해. 반드시 코드블럭 없이 JSON만 반환할 것.

{{
  "name_kr": "본문에서 순수 본명만 추출 (직무 꼬리표 붙이지 말 것). 못 찾으면 null",
  "phone": "010-XXXX-XXXX 형태 숫자만. 못 찾으면 null",
  "email": "이메일주소. 못 찾으면 null",
  "birth_year": 출생연도 숫자 4자리 (예: 1990). 못 찾으면 null,
  "summary": "주요 경력 2줄 요약 (전화번호/이메일/주소/생년월일 등 개인정보 절대 포함 금지!!!)",
  "sector": "가장 관련 깊은 도메인/산업분야 분류 (예: SW, Finance, Marketing 등. 미분류 금지)",
  "education_json": [
    {{"school": "대학교 이상 학교명", "major": "전공", "degree": "학사/석사 등", "year": "졸업년도"}}
  ],
  "careers_json": [
    {{
      "company": "회사명",
      "title": "직책/부서",
      "start_date": "YYYY.MM",
      "end_date": "YYYY.MM (또는 현재)"
    }}
  ],
  "neo4j_edges": [
    {{
      "action": "BUILT|DESIGNED|MANAGED|ANALYZED|LAUNCHED|NEGOTIATED|GREW|SUPPORTED 중 택1",
      "skill": "아래 지시된 Skill 목록 중 택1",
      "confidence": 0.0 ~ 1.0,
      "evidence_span": "해당 판단을 내리게 된 본문 문구 복사"
    }}
  ]
}}

[Skill 목록]:
Payment_and_Settlement_System, Service_Planning, Product_Manager, Data_Pipeline_Construction, Data_Engineering, Data_Analysis,
Backend, Frontend, Machine_Learning, MLOps, DevOps, Financial_Accounting, Corporate_Strategic_Planning, 사업개발_BD, 퍼포먼스마케팅,
Treasury_Management, FX_Dealing, Corporate_Funding, IPO_Preparation_and_Execution, Recruiting_and_Talent_Acquisition,
Organizational_Development, B2B영업, 물류_Logistics, Backend_Python, Backend_Java, Backend_Go, Backend_Node,
Kubernetes, Infrastructure_and_Cloud, 보안_Security, FinTech, Natural_Language_Processing, 컴퓨터비전_CV, 추천시스템,
Deep_Learning, Corporate_Legal_Counsel, Intellectual_Property, Legal_Compliance, Contract_Management, Litigation,
Network_on_Chip, Chiplet_Architecture, PIM_and_AI_Memory_Architecture, High_Performance_Computing, Automotive_Software, Automotive_Compliance, Rust, CUDA, GPU_Acceleration

이력서 본문:
{text}
"""

conn = sqlite3.connect('candidates.db')
cur = conn.cursor()

with driver.session() as session:
    for name, cid in targets:
        print(f"Re-parsing and syncing {name} ({cid})...")
        cur.execute('SELECT raw_text, name_kr, current_company, email, phone, profile_summary, total_years, sector FROM candidates WHERE id=?', (cid,))
        row = cur.fetchone()
        if not row or not row[0]:
            print(f"[{name}] No text found in SQLite")
            continue
            
        raw_text = row[0]
        company = row[2]
        email = row[3]
        phone = row[4]
        summary = row[5]
        years = row[6]
        sector = row[7]
        
        parsed = None
        for attempt in range(3):
            try:
                prompt = MEGA_PROMPT.replace("{text}", raw_text[:6000])
                res = model.generate_content(prompt)
                raw_json = res.text.replace("```json", "").replace("```", "").strip()
                parsed = json.loads(raw_json)
                break
            except Exception as e:
                print(f"  Attempt {attempt+1} failed: {e}")
                time.sleep(2)
                
        if not parsed:
            print(f"  [{name}] LLM parsing failed completely.")
            continue
            
        print(f"  Parsed successfully. Neo4j Edges: {len(parsed.get('neo4j_edges', []))}")
        
        # 1. Update SQLite with LLM parsed info if missing or outdated (optional, but keep it consistent)
        cur.execute("""
            UPDATE candidates 
            SET profile_summary=?, careers_json=?, education_json=?, updated_at=datetime('now')
            WHERE id=?
        """, (parsed.get("summary", summary), json.dumps(parsed.get("careers_json", []), ensure_ascii=False), 
              json.dumps(parsed.get("education_json", []), ensure_ascii=False), cid))
        conn.commit()
        
        # 2. Re-create Candidate Node in Neo4j
        session.run("""
            MERGE (c:Candidate {id: $id})
            SET c.name = $name, c.current_company = $company, c.email = $email,
                c.phone = $phone, c.profile_summary = $summary, c.total_years = $years, c.sector = $sector
        """, id=cid, name=parsed.get("name_kr") or name, company=company, email=email, phone=phone, 
             summary=parsed.get("summary", summary), years=years, sector=parsed.get("sector", sector))
             
        # 3. Clear old skill relationships
        session.run("MATCH (c:Candidate {id: $id})-[r]->(s:Skill) DELETE r", id=cid)
        
        # 4. Add the clean LLM-parsed edges
        edge_count = 0
        for edge in parsed.get("neo4j_edges", []):
            act = edge.get("action")
            skill = edge.get("skill")
            conf = float(edge.get("confidence", 1.0))
            ev = edge.get("evidence_span", "")
            
            if act and skill:
                normalized = normalize_skill(skill)
                session.run(f"""
                    MERGE (c:Candidate {{id: $id}})
                    MERGE (s:Skill {{name: $skill}})
                    MERGE (c)-[r:{act}]->(s)
                    SET r.confidence = $conf, r.evidence_span = $ev, r.source = 'llm_reparse'
                """, id=cid, skill=normalized, conf=conf, ev=ev)
                edge_count += 1
                
        print(f"  Sync complete: Created {edge_count} clean edges in Neo4j.")

conn.close()
driver.close()
print("All target candidates have been cleanly parsed and synced.")
