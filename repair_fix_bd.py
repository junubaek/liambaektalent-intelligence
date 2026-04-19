import sqlite3
import json
from google import genai
from google.genai import types
from neo4j import GraphDatabase

with open("C:/Users/cazam/Downloads/이력서자동분석검색시스템/secrets.json", "r") as f:
    secrets = json.load(f)

client = genai.Client(api_key=secrets["GEMINI_API_KEY"])
driver = GraphDatabase.driver("neo4j://127.0.0.1:7687", auth=("neo4j", "toss1234"))

prompt_template = """
이력서 내용에서 신사업, 사업개발, 파트너십 유치 등과 관련된 비즈니스 부문 업무 경험을 추출하세요.
(예: 신사업 기획, 제휴/파트너십, Business Development, BD 등)

만약 1건이라도 있다면 무조건 아래 JSON 포맷을 반환하세요.
[
    {{"action": "MANAGED", "skill": "Business_Development", "weight": 1.0}}
]
(반드시 skill은 "Business_Development" 로 통일하세요)

없으면 [] 반환.

이력서 내역:
"{resume_text}"
"""

def extract_edges(raw_text):
    prompt = prompt_template.format(resume_text=raw_text[:4000])
    config = types.GenerateContentConfig(temperature=0.0)
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config=config
        )
        raw_str = response.text.strip()
        if raw_str.startswith("```json"): raw_str = raw_str[7:]
        elif raw_str.startswith("```"): raw_str = raw_str[3:]
        if raw_str.endswith("```"): raw_str = raw_str[:-3]
        return json.loads(raw_str.strip())
    except Exception as e:
        print("Error:", e)
        return []

conn = sqlite3.connect('C:/Users/cazam/Downloads/이력서자동분석검색시스템/candidates.db')
c = conn.cursor()
c.execute("""
SELECT name_kr, raw_text FROM candidates
WHERE raw_text LIKE '%사업개발%'
   OR raw_text LIKE '%신사업%'
   OR raw_text LIKE '%파트너십%'
   OR raw_text LIKE '%Business Development%'
   OR raw_text LIKE '% BD %'
""")
rows = c.fetchall()
conn.close()

valid_added = 0
for name_kr, raw_text in rows:
    edges = extract_edges(raw_text)
    if edges:
        with driver.session() as session:
            query = """
            MATCH (c:Candidate) WHERE c.name CONTAINS $name_kr
            MERGE (s:Skill {name: 'Business_Development'})
            MERGE (c)-[r:MANAGED]->(s)
            ON CREATE SET r.weight = 1.0, r.source = 'deep_repair_bd'
            ON MATCH SET r.weight = 1.0, r.source = 'deep_repair_bd'
            RETURN count(r)
            """
            res = session.run(query, name_kr=name_kr)
            for rec in res:
                valid_added += rec[0]

print(f"Added additional BD Edges: {valid_added}")
