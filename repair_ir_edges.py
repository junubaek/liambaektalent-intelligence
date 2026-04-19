import os
import json
import sqlite3
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from google import genai
from google.genai import types
from neo4j import GraphDatabase

# Secrets
with open("C:/Users/cazam/Downloads/이력서자동분석검색시스템/secrets.json", "r") as f:
    secrets = json.load(f)

# Gemini Config
client = genai.Client(api_key=secrets["GEMINI_API_KEY"])
MODEL_ID = "gemini-2.5-flash"  # Flash Lite is essentially Flash in 2.x

# Neo4j Config
neo4j_uri = "neo4j://127.0.0.1:7687"
neo4j_auth = ("neo4j", "toss1234")
    
prompt_template = """
당신은 헤드헌터 AI입니다. 
아래 이력서 내용에서 오직 'IR(투자자관계), 공시, 주주총회, Investor Relations'와 관련된 업무 경험만 찾아서 역량(Skill) 엣지로 추출해주세요.
다른 재무/회계/영업 경험은 무시하세요. 오직 IR 관련 경험만 중요합니다.

출력 포맷 (JSON 배열):
[
    {{"action": "MANAGED", "skill": "Investor_Relations", "weight": 1.0, "is_mandatory": true}}
]

* 주의: 
- IR 관련 경험이 이력서에 전혀 없거나 모호하면 빈 배열 [] 을 반환하세요.
- skill 이름은 반드시 "Investor_Relations" 이어야 합니다.
- 마크다운이나 부가 설명 없이 JSON 배열만 출력하세요.

이력서 내역:
"{resume_text}"
"""

def extract_ir_edges(raw_text):
    prompt = prompt_template.format(resume_text=raw_text)
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
        print(f"Gemini API Error: {str(e)}")
        return []

def process_candidate(candidate, driver):
    cid, name_kr, raw_text = candidate
    if not raw_text:
        return 0

    edges = extract_ir_edges(raw_text)
    if not edges:
        return 0
        
    valid_edges = 0
    with driver.session() as session:
        for edge in edges:
            skill = edge.get("skill")
            action = edge.get("action", "MANAGED")
            weight = edge.get("weight", 1.0)
            
            if skill in ["Investor_Relations", "IR", "Investor Relations", "IR_Management"]:
                skill = "Investor_Relations" # Standardize
                
                # We use MERGE to add the edge without removing others
                # But Neo4j id must match. Let's try matching by c.id first.
                # In this db, c.id is the unique identifier.
                query = f"""
                MATCH (c:Candidate)
                WHERE c.name CONTAINS $name_kr
                MERGE (s:Skill {{name: $skill}})
                MERGE (c)-[r:{action}]->(s)
                ON CREATE SET r.weight = $weight, r.source = 'deep_repair_ir'
                ON MATCH SET r.weight = $weight, r.source = 'deep_repair_ir'
                RETURN count(r)
                """
                res = session.run(query, name_kr=name_kr, skill=skill, weight=float(weight))
                for rec in res:
                    valid_edges += rec[0]
                
    return valid_edges

def main():
    conn = sqlite3.connect('C:/Users/cazam/Downloads/이력서자동분석검색시스템/candidates.db')
    c = conn.cursor()
    c.execute("""
        SELECT id, name_kr, raw_text FROM candidates
        WHERE raw_text LIKE '%IR%'
           OR raw_text LIKE '%투자자관계%'
           OR raw_text LIKE '%Investor Relations%'
    """)
    candidates = c.fetchall()
    conn.close()
    
    print(f"Total candidates to inspect: {len(candidates)}")
    
    driver = GraphDatabase.driver(neo4j_uri, auth=neo4j_auth)
    
    total_added = 0
    # Process sequentially or lightly parallel
    start_time = time.time()
    
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = [executor.submit(process_candidate, cand, driver) for cand in candidates]
        for i, future in enumerate(as_completed(futures)):
            added = future.result()
            total_added += added
            if (i + 1) % 10 == 0:
                print(f"Processed {i+1}/{len(candidates)} ... Added so far: {total_added}")

    # Check total edges for Investor_Relations
    with driver.session() as session:
        res = session.run("MATCH (c:Candidate)-[r]->(s:Skill {name: 'Investor_Relations'}) RETURN count(r) as total")
        total_ir = res.single()['total']
        print(f"\\n✅ Deep repair complete. Added edges: {total_added}")
        print(f"🎯 Total Investor_Relations edges in DB now: {total_ir}")
        
    driver.close()
    print(f"Time taken: {time.time() - start_time:.1f}s")

if __name__ == "__main__":
    main()
