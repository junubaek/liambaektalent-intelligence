import sqlite3
import json
import time
import sys
import re
from google import genai
from google.genai import types

sys.stdout.reconfigure(encoding='utf-8')

# --- 1. Load Secrets & Init Gemini ---
with open("secrets.json", "r", encoding="utf-8") as f:
    secrets = json.load(f)
client = genai.Client(api_key=secrets["GEMINI_API_KEY"])

# --- 2. Extract Unique Companies ---
db = sqlite3.connect('candidates.db')
c = db.cursor()
c.execute("SELECT careers_json FROM candidates WHERE careers_json IS NOT NULL")
rows = c.fetchall()

companies = set()
for r in rows:
    careers_json = r[0]
    try:
        arr = json.loads(careers_json)
        if isinstance(arr, list) and arr and isinstance(arr[0], dict):
            comp = arr[0].get('company', '').strip()
            if comp and comp != '미상':
                companies.add(comp)
    except:
        pass

companies_list = list(companies)
print(f"Total Unique Companies to classify: {len(companies_list)}", flush=True)

# --- 3. Gemini Classification in batches ---
from neo4j import GraphDatabase
driver = GraphDatabase.driver("bolt://127.0.0.1:7687", auth=("neo4j", "toss1234"))

model = "gemini-2.5-flash"
config = types.GenerateContentConfig(
    response_mime_type="application/json",
    temperature=0.1
)

batch_size = 150
total_updated = 0

for i in range(0, len(companies_list), batch_size):
    batch = companies_list[i:i+batch_size]
    print(f"Processing batch {i//batch_size + 1}: {len(batch)} companies...", flush=True)
    
    prompt = f"""
    다음은 이력서에 기재된 회사명 목록입니다. 각 회사명을 키(문자열)로, 다음 5가지 카테고리 중 단 하나를 값(문자열)으로 엄격하게 분류하여 JSON 형식으로 반환하세요.
    카테고리: "대기업", "스타트업", "중견기업", "중소기업", "금융/컨설팅 기업"
    
    출력 형식 예시:
    {{
      "삼성전자": "대기업",
      "비바리퍼블리카": "스타트업",
      "우리은행": "금융/컨설팅 기업"
    }}
    
    회사 목록:
    {chr(10).join(batch)}
    """
    
    try:
        response = client.models.generate_content(model=model, contents=prompt, config=config)
        
        # Clean JSON 
        raw_text = response.text.replace('```json', '').replace('```', '').strip()
        class_map = json.loads(raw_text)
        
        # Update Neo4j
        with driver.session() as s:
            for comp, scale in class_map.items():
                if scale not in ["대기업", "스타트업", "중견기업", "중소기업", "금융/컨설팅 기업"]:
                    scale = "중소기업" 
                    
                s.run(
                    "MATCH (c:Candidate {company: $company}) "
                    "SET c.company_scale = $scale",
                    company=comp, scale=scale
                )
                total_updated += 1
                
    except Exception as e:
        print(f"Error on batch: {e}", flush=True)
        time.sleep(2)

print(f"Neo4j Update completed. Updated nodes: {total_updated}", flush=True)
driver.close()
db.close()
