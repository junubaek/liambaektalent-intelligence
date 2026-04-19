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
이력서 내용에서 재무 및 기획과 관련된 업무 경험을 추출하세요.
(예: 재무기획, 예산 수립/관리, 관리회계, 경영분석, KPI, 투자타당성 분석, FP&A 등)

만약 1건이라도 있다면 무조건 아래 JSON 포맷을 반환하세요.
[
    {{"action": "MANAGED", "skill": "FP_and_A", "weight": 1.0}}
]
(반드시 skill은 "FP_and_A" 로 통일하세요)

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
WHERE raw_text LIKE '%FP&A%'
   OR raw_text LIKE '%FP%A%'
   OR raw_text LIKE '%재무기획%'
   OR raw_text LIKE '%예산기획%'
""")
rows = c.fetchall()
conn.close()

print(f"FP&A Target Candidates: {len(rows)}")

valid_added = 0
for name_kr, raw_text in rows:
    edges = extract_edges(raw_text)
    if edges:
        with driver.session() as session:
            # We use FP_and_A to avoid exact string API issues
            query = """
            MATCH (c:Candidate) WHERE c.name CONTAINS $name_kr
            MERGE (s:Skill {name: 'FP_and_A'})
            MERGE (c)-[r:MANAGED]->(s)
            ON CREATE SET r.weight = 1.0, r.source = 'deep_repair_fpa'
            ON MATCH SET r.weight = 1.0, r.source = 'deep_repair_fpa'
            RETURN count(r)
            """
            res = session.run(query, name_kr=name_kr)
            for rec in res:
                valid_added += rec[0]

print(f"Added FP&A (FP_and_A) Edges: {valid_added}")
