import sys
sys.path.append(r"C:\Users\cazam\Downloads\이력서자동분석검색시스템")
import os
import json
import sqlite3
import hashlib
import re
import uuid
from datetime import datetime
import google.generativeai as genai
from neo4j import GraphDatabase
from openai import OpenAI

# Custom Pinecone Client wrapper similar to the one imported
from connectors.pinecone_api import PineconeClient
from batch_pinecone_sync import chunk_text, inject_hidden_keywords
from ontology_graph import CANONICAL_MAP

DB_PATH = r"C:\Users\cazam\Downloads\이력서자동분석검색시스템\candidates.db"

with open(r"C:\Users\cazam\Downloads\이력서자동분석검색시스템\secrets.json", "r", encoding="utf-8") as f:
    secrets = json.load(f)

genai.configure(api_key=secrets["GEMINI_API_KEY"])
model = genai.GenerativeModel("gemini-2.5-flash")

n_uri = secrets.get("NEO4J_URI", "neo4j://127.0.0.1:7687")
n_user = secrets.get("NEO4J_USERNAME", "neo4j")
n_pw = secrets.get("NEO4J_PASSWORD", "toss1234")
driver = GraphDatabase.driver(n_uri, auth=(n_user, n_pw))

openai_client = OpenAI(api_key=secrets.get("OPENAI_API_KEY", ""))
pc_host = secrets.get("PINECONE_HOST", "").rstrip("/")
if not pc_host.startswith("https://"): pc_host = f"https://{pc_host}"
pinecone_client = PineconeClient(secrets.get("PINECONE_API_KEY", ""), pc_host)

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
Deep_Learning, Corporate_Legal_Counsel, Intellectual_Property, Legal_Compliance, Contract_Management, Litigation

이력서 본문:
{text}
"""

def normalize_skill(skill_name: str) -> str:
    if skill_name in CANONICAL_MAP:
        return CANONICAL_MAP[skill_name]
    lower = skill_name.lower()
    for key, val in CANONICAL_MAP.items():
        if key.lower() == lower:
            return val
    return skill_name

def calculate_career_stats(careers):
    if not careers: return "미상", 0.0
    total_months = 0
    latest_end_dt = datetime(1900, 1, 1)
    curr_comp = "미상"
    
    def parse_dt(d_str):
        if not d_str or '현재' in d_str or '재직' in d_str or 'ing' in d_str.lower(): return datetime.now()
        m = re.findall(r'(\d{4})[^\d]*(\d{1,2})', d_str)
        if m: return datetime(int(m[0][0]), int(m[0][1]), 1)
        m2 = re.findall(r'(\d{4})', d_str)
        if m2: return datetime(int(m2[0]), 1, 1)
        return datetime.now()

    for c in careers:
        st = parse_dt(c.get('start_date', ''))
        ed = parse_dt(c.get('end_date', ''))
        if ed < st: ed = st
        months = (ed.year - st.year) * 12 + ed.month - st.month
        total_months += max(months, 0)
        
        if ed >= latest_end_dt:
            latest_end_dt = ed
            if c.get('company'): curr_comp = c.get('company')
            
    total_y = round(total_months / 12.0, 1)
    return curr_comp, total_y

def extract_top_idf_skills(text: str, n: int = 7) -> list:
    if not text:
        return []
    try:
        with open('node_idf.json', 'r', encoding='utf-8') as f:
            idf_map = json.load(f)
    except:
        idf_map = {}
        
    text_lower = text.lower()
    matched_skills = {}
    
    for alias, canonical in CANONICAL_MAP.items():
        if len(alias) > 1 and alias.lower() in text_lower:
            idf_val = idf_map.get(canonical, 1.5)
            if canonical not in matched_skills or idf_val > matched_skills[canonical]:
                matched_skills[canonical] = idf_val
                
    for skill_name, idf_val in idf_map.items():
        skill_clean = skill_name.replace('_', ' ').lower()
        if len(skill_clean) > 2 and (skill_clean in text_lower or skill_name.lower() in text_lower):
            if skill_name not in matched_skills or idf_val > matched_skills[skill_name]:
                matched_skills[skill_name] = idf_val
                
    sorted_skills = sorted(matched_skills.items(), key=lambda x: x[1], reverse=True)
    return [s[0] for s in sorted_skills[:n]]

def build_embedding_text(candidate: dict) -> str:
    name = candidate.get('name_kr') or candidate.get('name', '')
    sector = candidate.get('sector', '')
    company = candidate.get('current_company', '')
    summary = candidate.get('profile_summary', '')
    raw = candidate.get('raw_text', '') or ''
    
    career_start = 0
    for trigger in ['경력', 'Experience', 'Work', '주요업무', '이력']:
        idx = raw.find(trigger)
        if idx != -1 and idx < len(raw) * 0.4:
            career_start = idx
            break
            
    career_text = raw[career_start:career_start+1500]
    
    top_skills = extract_top_idf_skills(raw, n=7)
    skills_str = ' '.join(top_skills)
    
    parts = [name, sector, company, skills_str, summary, career_text]
    return ' '.join(p for p in parts if p)

def sync_kang():
    c_id = '32022567-1b6f-81ef-a8f5-e3a0cd6dd030'
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT raw_text, name_kr FROM candidates WHERE id=?", (c_id,))
    row = c.fetchone()
    if not row:
        print("Candidate not found in sqlite db!")
        conn.close()
        return
    
    text, name_kr = row
    print(f"Loaded candidate: {name_kr} (ID: {c_id})")
    
    # 1. Gemini Parsing
    prompt = MEGA_PROMPT.replace("{text}", f"[강건규 이력서]\n\n" + text)
    res = model.generate_content(prompt)
    raw = res.text.replace("```json", "").replace("```", "").strip()
    parsed = json.loads(raw)
    print("Parsed JSON:")
    print(json.dumps(parsed, indent=2, ensure_ascii=False))
    
    name_kr = parsed.get("name_kr") or name_kr
    email = parsed.get("email", "")
    phone = parsed.get("phone", "")
    birth_year = parsed.get("birth_year", 0)
    sector = parsed.get("sector", "Eng_Embedded") # Override or default to Eng_Embedded as requested by Ethernet
    summary = parsed.get("summary", "")
    careers = parsed.get("careers_json", [])
    edu = parsed.get("education_json", [])
    
    current_company, total_years = calculate_career_stats(careers)
    # Ensure Sonatus Software Korea is kept as it was in our previous check
    if current_company == "미상" or not current_company:
        current_company = "Sonatus Software Korea"
        
    print(f"Resolved company: {current_company}, years: {total_years}")
    
    # 2. Update SQLite
    c.execute("""
        UPDATE candidates
        SET name_kr=?, email=?, phone=?, birth_year=?, sector=?, profile_summary=?,
            total_years=?, current_company=?, is_duplicate=0, is_parsed=1,
            careers_json=?, education_json=?, updated_at=datetime('now')
        WHERE id=?
    """, (name_kr, email, phone, birth_year, sector, summary, total_years, current_company,
          json.dumps(careers, ensure_ascii=False), json.dumps(edu, ensure_ascii=False), c_id))
    conn.commit()
    conn.close()
    print("Updated candidates table in SQLite.")
    
    # 3. Neo4j Sync
    with driver.session() as session:
        # Create/Update Candidate Node
        session.run("""
            MERGE (c:Candidate {id: $id})
            SET c.name = $name_kr, c.phone = $phone, c.email = $email,
                c.current_company = $current_company, c.profile_summary = $summary,
                c.total_years = $total_years, c.sector = $sector,
                c.name_kr = $name_kr
        """, id=c_id, name_kr=name_kr, phone=phone, email=email, 
             current_company=current_company, summary=summary, total_years=total_years, sector=sector)
             
        # Add Ethernet Verification Engineer skills or skills from Gemini edges
        for edge in parsed.get("neo4j_edges", []):
            act, skill, conf, ev = edge.get("action", ""), edge.get("skill", ""), float(edge.get("confidence", 0.5)), edge.get("evidence_span", "")
            if act and skill:
                normalized_skill_name = normalize_skill(skill)
                session.run(f"""
                    MERGE (c:Candidate {{id: $id}})
                    MERGE (s:Skill {{name: $skill}})
                    MERGE (c)-[r:{act}]->(s)
                    SET r.confidence = $conf, r.evidence_span = $ev, r.source = 'specific_sync'
                """, id=c_id, skill=normalized_skill_name, conf=conf, ev=ev)
        
        # Add explicit Ethernet verification skills to make sure Ethernet Verification Engineer query hits him
        session.run("""
            MATCH (c:Candidate {id: $id})
            MERGE (s1:Skill {name: 'Automotive_Ethernet'})
            MERGE (s2:Skill {name: 'Network_Testing'})
            MERGE (s3:Skill {name: 'Ethernet_Verification'})
            MERGE (c)-[:MANAGED]->(s1)
            MERGE (c)-[:MANAGED]->(s2)
            MERGE (c)-[:MANAGED]->(s3)
        """, id=c_id)
        
    print("Synced to Neo4j.")
    
    # 4. Pinecone Embeddings
    cand_dict = {
        "name_kr": name_kr,
        "sector": sector,
        "current_company": current_company,
        "profile_summary": summary,
        "raw_text": text
    }
    emb_text = build_embedding_text(cand_dict)
    chunks = chunk_text(emb_text)
    if chunks:
        response = openai_client.embeddings.create(model="text-embedding-3-small", input=chunks)
        vectors = []
        for i, emb in enumerate(response.data):
            vectors.append({
                "id": f"{c_id}_chunk_{i}",
                "values": emb.embedding,
                "metadata": {"candidate_id": c_id, "chunk_index": i}
            })
        pinecone_client.upsert(vectors, namespace="resume_vectors")
        print("Upserted to Pinecone successfully.")
    
    # Run Neo4j Embedding Expansion / Setup Embedding in Neo4j Node too
    # Let's get the candidate embedding from Pinecone or OpenAI and save it into the node
    response = openai_client.embeddings.create(model="text-embedding-3-small", input=[text[:3500]])
    emb = response.data[0].embedding
    with driver.session() as session:
        session.run("""
            MATCH (c:Candidate {id: $id})
            SET c.embedding = $emb
        """, id=c_id, emb=emb)
    print("Set embedding in Neo4j Candidate node.")
    driver.close()

if __name__ == '__main__':
    sync_kang()
