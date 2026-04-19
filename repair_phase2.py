import os
import json
import sqlite3
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from google import genai
from google.genai import types
from neo4j import GraphDatabase

# Config
with open("secrets.json", "r") as f:
    secrets = json.load(f)

client = genai.Client(api_key=secrets["GEMINI_API_KEY"])
MODEL_ID = "gemini-2.5-flash"

neo4j_uri = "neo4j://127.0.0.1:7687"
neo4j_auth = ("neo4j", "toss1234")

# 6 New Phase 2 Nodes
NODE_MAP = {
    "Management_Accounting": ["관리회계", "원가회계", "Costing", "손익 분석", "원가 절감", "BEP 분석", "표준원가"],
    "CRM_Marketing": ["CRM", "고객관계관리", "리텐션 마케팅", "VIP 마케팅", "Braze", "마케팅 자동화"],
    "Content_Marketing": ["콘텐츠 마케팅", "SNS 채널 운영", "인플루언서 협업", "유튜브 기획"],
    "Talent_Acquisition": ["채용", "리크루팅", "TA", "다이렉트 소싱", "채용 브랜딩", "온보딩"],
    "Compensation_and_Benefits": ["C&B", "Comp&Ben", "Payroll", "4대보험", "연말정산", "인센티브 제도"],
    "Employee_Relations": ["노무", "ER", "노사 관계", "근로기준법", "취업규칙 개정", "노동청 대응"]
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
- skill 이름은 반드시 지정된 타겟 역량 목록 중에서만 정확히 일치하는 문자열을 골라서 사용해야 합니다.
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
                
            if skill in target_skills:
                query = f"""
                MATCH (c:Candidate)
                WHERE c.name CONTAINS $name_kr
                MERGE (s:Skill {{name: $skill}})
                MERGE (c)-[r:{action}]->(s)
                ON CREATE SET r.weight = $weight, r.source = 'deep_repair_phase2'
                ON MATCH SET r.weight = $weight, r.source = 'deep_repair_phase2'
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
    conn = sqlite3.connect('candidates_copy.db') # Read from copy to skip locks!
    c = conn.cursor()
    c.execute("SELECT name_kr, raw_text FROM candidates WHERE raw_text IS NOT NULL")
    rows = c.fetchall()
    conn.close()
    
    candidates_to_process = []
    
    for row in rows:
        name_kr, raw_text = row
        if not name_kr: continue
        
        c_targets = set()
        for node, keywords in NODE_MAP.items():
            for kw in keywords:
                if kw.lower() in raw_text.lower():
                    c_targets.add(node)
                    break
                    
        if c_targets:
            candidates_to_process.append((name_kr, raw_text, list(c_targets)))
            
    print(f"Total candidates matching any of 6 domains: {len(candidates_to_process)}")
    
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
            if total_processed % 50 == 0:
                print(f"Processed {total_processed}/{len(candidates_to_process)} ...")

    print("\\n### 💡 복구 결과 테이블 (Deep Repair Phase 2)")
    print("| 노드(Skill) | 복구(추가)된 엣지 수 |")
    print("| :--- | :--- |")
    
    sorted_nodes = sorted(node_counts.items(), key=lambda x: -x[1])
    for s_name, s_count in sorted_nodes:
        print(f"| {s_name} | {s_count} 개 |")
        
    print(f"\\nTime taken: {time.time() - start_time:.1f}s")
    driver.close()

if __name__ == "__main__":
    main()
