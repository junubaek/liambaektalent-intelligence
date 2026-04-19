import os
import json
import hashlib
import pdfplumber
from docx import Document
from neo4j import GraphDatabase
from google import genai
from google.genai import types
from pydantic import BaseModel, Field
from typing import List, Optional
from tqdm import tqdm

FOLDER1 = r"C:\Users\cazam\Downloads\02_resume 전처리"
FOLDER2 = r"C:\Users\cazam\Downloads\02_resume_converted_docx"
FOLDER3 = r"C:\Users\cazam\Downloads\02_resume_converted_v8"

TARGET_NODES = {
    "IR": ["IR", "투자자", "주주", "NDR", "공시", "자본시장", "Investor Relations"],
    "Business_Development": ["사업개발", "BD", "파트너십", "신사업", "제휴", "Business Development"],
    "Brand_Management": ["브랜드", "Brand", "IMC", "포지셔닝", "브랜딩"],
    "SCM": ["SCM", "공급망", "물류", "구매", "조달", "재고"],
    "Legal_Compliance": ["법무", "규제", "컴플라이언스", "준법", "계약", "소송"],
    "HR_Strategic_Planning": ["인사기획", "HR 전략", "조직설계", "핵심인재"],
    "Performance_and_Compensation": ["평가보상", "C&B", "인센티브", "연봉", "급여"],
    "Talent_Acquisition": ["채용", "TA", "리크루팅", "소싱", "헤드헌팅"],
    "Employee_Relations": ["노무", "ER", "노사", "근로기준법", "노동청"],
    "CRM_Marketing": ["CRM", "리텐션", "VIP", "고객관계관리", "Braze"],
    "Management_Accounting": ["관리회계", "원가", "CVP", "제조원가", "BEP"],
    "Content_Marketing": ["콘텐츠", "유튜브", "SNS", "바이럴"],
    "ESG": ["ESG", "지속가능경영", "탄소중립", "친환경"]
}

def collect_files():
    files = {}
    for folder in [FOLDER1, FOLDER2, FOLDER3]:
        if os.path.exists(folder):
            for f in os.listdir(folder):
                if f.endswith((".pdf", ".docx", ".doc")):
                    base_name = f.rsplit(".", 1)[0]
                    if base_name not in files:
                        files[base_name] = os.path.join(folder, f)
    return files

def extract_text(filepath):
    ext = filepath.rsplit(".", 1)[-1].lower()
    try:
        if ext == "pdf":
            with pdfplumber.open(filepath) as pdf:
                return "\n".join([page.extract_text() or "" for page in pdf.pages])
        elif ext in ("docx", "doc"):
            doc = Document(filepath)
            return "\n".join(p.text for p in doc.paragraphs)
    except:
        pass
    return ""

def main():
    print("🚀 [Deep Repair] Starting 13-node backfill repair pipeline...")
    with open("secrets.json", "r", encoding="utf-8") as f:
        secrets = json.load(f)
        
    client = genai.Client(api_key=secrets["GEMINI_API_KEY"])
    driver = GraphDatabase.driver("neo4j://127.0.0.1:7687", auth=("neo4j", "toss1234"))
    
    files = collect_files()
    repair_targets = {}
    
    print("🔍 Scanning all local texts for keywords...")
    for name, filepath in tqdm(files.items(), desc="Keyword Scan"):
        text = extract_text(filepath)
        if not text: continue
        
        matched_nodes = []
        text_lower = text.lower()
        for node, keywords in TARGET_NODES.items():
            for kw in keywords:
                if kw.lower() in text_lower:
                    matched_nodes.append(node)
                    break
                    
        if matched_nodes:
            repair_targets[name] = {"text": text, "nodes": matched_nodes}
            
    print(f"\n🎯 Found {len(repair_targets)} files with candidate keywords! Executing targeted LLM parse via Gemini.")
    
    recovered_stats = {node: 0 for node in TARGET_NODES.keys()}
    
    for name, obj in tqdm(repair_targets.items(), desc="LLM Deep Repair"):
        matched_nodes = obj["nodes"]
        text = obj["text"]
        doc_hash = hashlib.sha256(text.encode('utf-8')).hexdigest()
        
        class RepairedEdge(BaseModel):
            action: str = Field(description="One of: MANAGED, EXECUTED, PLANNED, DESIGNED, OPTIMIZED, ANALYZED")
            skill: str = Field(description=f"MUST BE ONE OF THESE EXACT STRINGS: {matched_nodes}. Do not invent skills.")

        class RepairExtraction(BaseModel):
            edges: list[RepairedEdge]
            
        prompt = f"""
Candidate Resume:
{text[:20000]}

Instruction: 
Carefully extract any professional capabilities focusing ONLY on these domains: {matched_nodes}.
Use the exact domain string for the 'skill'.
If the candidate has strong experience in the domain, return an edge. If not, return an empty edges list.
"""
        
        try:
            response = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=RepairExtraction,
                    temperature=0.0,
                )
            )
            data = json.loads(response.text)
            edges = data.get("edges", [])
        except Exception as e:
            # Maybe schema fail or API rate limit. Skip.
            continue
            
        if not edges: continue
        
        # Merge exactly against the matching ID
        with driver.session() as session:
            for e in edges:
                action = e.get("action", "EXECUTED").upper()
                skill = e.get("skill")
                if skill not in matched_nodes: continue
                
                session.run(f"""
                    MATCH (c:Candidate {{id: $doc_hash}})
                    MERGE (s:Skill {{name: $skill}})
                    MERGE (c)-[r:{action}]->(s)
                    SET r.source = 'deep_repair_13', r.confidence = 1.0
                """, doc_hash=doc_hash, skill=skill)
                
                recovered_stats[skill] += 1
                
    print("\n✅ Deep Repair Completed!")
    print("="*40)
    print("📊 [Recovered Edge Counts per Node]")
    print("="*40)
    for node, count in sorted(recovered_stats.items(), key=lambda x: x[1], reverse=True):
        print(f"  - {node}: {count} edges recovered")
    print("="*40)

if __name__ == "__main__":
    main()
