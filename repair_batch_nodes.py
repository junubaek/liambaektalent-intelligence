import os
import json
import sqlite3
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from google import genai
from google.genai import types
from neo4j import GraphDatabase

# Config
with open("C:/Users/cazam/Downloads/이력서자동분석검색시스템/secrets.json", "r") as f:
    secrets = json.load(f)

client = genai.Client(api_key=secrets["GEMINI_API_KEY"])
MODEL_ID = "gemini-2.5-flash"

neo4j_uri = "neo4j://127.0.0.1:7687"
neo4j_auth = ("neo4j", "toss1234")

NODE_MAP = {
    "ESG": ["ESG", "지속가능경영"],
    "Compliance": ["컴플라이언스", "준법"],
    "FP&A": ["FP&A", "재무기획"],
    "Mergers_and_Acquisitions": ["M&A", "인수합병", "인수 합병"],
    "IPO_Management": ["IPO", "상장", "기업공개"],
    "Legal_Compliance": ["법무", "규제대응"],
    "Patent_Management": ["특허", "지재권", "지식재산권"],
    "HR_Strategic_Planning": ["인사기획", "HRD", "조직문화"],
    "Performance_and_Compensation": ["보상", "평가", "C&B"],
    "Brand_Management": ["브랜드", "브랜딩", "PR", "홍보"],
    "Performance_Marketing": ["퍼포먼스", "퍼포먼스마케팅", "CRM"],
    "Business_Development": ["사업개발", "BD", "신사업", "파트너십"],
    "SCM": ["SCM", "물류", "공급망"],
    "Procurement": ["구매", "소싱"]
}

prompt_template = """
당신은 최고의 헤드헌터 AI입니다. 
아래 이력서 내용에서 지정된 타겟 역량(Skill) 목록과 관련된 업무 경험만 찾아서 엣지로 추출해주세요.
다른 경험은 무시하세요.

타겟 역량 목록:
{target_list}

출력 포맷 (JSON 배열):
[
    {{"action": "MANAGED", "skill": "타겟 역량 이름", "weight": 1.0}}
]

* 주의 사항: 
- 이력서에 위 타겟 역량과 관련된 명확한 경험이 전혀 없으면 빈 배열 [] 을 반환하세요.
- skill 이름은 반드시 지정된 타겟 역량 목록 중에서만 정확히 일치하는 문자열을 골라서 사용해야 합니다. (예: "Mergers_and_Acquisitions", "FP&A" 등)
- 마크다운이나 기타 부가 설명 없이 JSON 배열만 출력하세요.

이력서 내역:
"{resume_text}"
"""

def extract_edges(raw_text, target_skills):
    prompt = prompt_template.format(
        target_list=", ".join(target_skills),
        resume_text=raw_text[:4000] # truncate safely
    )
    # Use temperature 0 for max determinism
    config = types.GenerateContentConfig(temperature=0.0)
    try:
        response = client.models.generate_content(
            model=MODEL_ID,
            contents=prompt,
            config=config
        )
        raw_str = response.text.strip()
        if raw_str.startswith("```json"): raw_str = raw_str[7:]
        elif raw_str.startswith("```"): raw_str = raw_str[3:]
        if raw_str.endswith("```"): raw_str = raw_str[:-3]
        
        parsed = json.loads(raw_str.strip())
        return parsed
    except Exception as e:
        print(f"Gemini API Error for targets {target_skills}: {str(e)}")
        return []

def process_candidate(candidate, target_skills, driver):
    name_kr, raw_text = candidate
    if not raw_text:
        return []

    edges = extract_edges(raw_text, target_skills)
    if not edges:
        return []
        
    valid_added = []
    with driver.session() as session:
        for edge in edges:
            skill = edge.get("skill")
            action = edge.get("action", "MANAGED")
            weight = float(edge.get("weight", 1.0))
            
            valid_actions = ["BUILT", "DESIGNED", "MANAGED", "ANALYZED", "LAUNCHED", "NEGOTIATED", "GREW", "SUPPORTED"]
            if action not in valid_actions:
                action = "MANAGED"
                
            # double check if skill is in requested targets to prevent hallucination
            if skill in target_skills:
                query = f"""
                MATCH (c:Candidate)
                WHERE c.name CONTAINS $name_kr
                MERGE (s:Skill {{name: $skill}})
                MERGE (c)-[r:{action}]->(s)
                ON CREATE SET r.weight = $weight, r.source = 'deep_repair_batch'
                ON MATCH SET r.weight = $weight, r.source = 'deep_repair_batch'
                RETURN count(r)
                """
                res = session.run(query, name_kr=name_kr, skill=skill, weight=weight)
                cnt = 0
                for rec in res:
                    cnt += rec[0]
                if cnt > 0:
                    valid_added.append(skill)
                    
    return valid_added

def main():
    conn = sqlite3.connect('C:/Users/cazam/Downloads/이력서자동분석검색시스템/candidates.db')
    c = conn.cursor()
    c.execute("SELECT name_kr, raw_text FROM candidates WHERE raw_text IS NOT NULL")
    rows = c.fetchall()
    conn.close()
    
    # 1. Keyword based candidate extraction
    candidates_to_process = []
    
    for row in rows:
        name_kr, raw_text = row
        if not name_kr: continue
        
        c_targets = set()
        for node, keywords in NODE_MAP.items():
            for kw in keywords:
                if kw.lower() in raw_text.lower():
                    c_targets.add(node)
                    break # move to next node if hit
                    
        if c_targets:
            candidates_to_process.append((name_kr, raw_text, list(c_targets)))
            
    print(f"Total candidates matching any of 14 domains: {len(candidates_to_process)}")
    
    driver = GraphDatabase.driver(neo4j_uri, auth=neo4j_auth)
    
    node_counts = {node: 0 for node in NODE_MAP.keys()}
    total_processed = 0
    start_time = time.time()
    
    with ThreadPoolExecutor(max_workers=30) as executor:
        futures = []
        for cand in candidates_to_process:
            name_kr, raw_text, targets = cand
            f = executor.submit(process_candidate, (name_kr, raw_text), targets, driver)
            futures.append(f)
            
        for future in as_completed(futures):
            added_skills = future.result()
            for s in added_skills:
                if s in node_counts:
                    node_counts[s] += 1
            
            total_processed += 1
            if total_processed % 100 == 0:
                print(f"Processed {total_processed}/{len(candidates_to_process)} ...")

    # Output Results as MD Table natively
    print("\\n### 💡 복구 결과 테이블 (Deep Repair)")
    print("| 노드(Skill) | 복구(추가)된 엣지 수 |")
    print("| :--- | :--- |")
    
    # sort by count desc
    sorted_nodes = sorted(node_counts.items(), key=lambda x: -x[1])
    for s_name, s_count in sorted_nodes:
        print(f"| {s_name} | {s_count} 개 |")
        
    print(f"\\nTime taken: {time.time() - start_time:.1f}s")
    driver.close()

if __name__ == "__main__":
    main()
