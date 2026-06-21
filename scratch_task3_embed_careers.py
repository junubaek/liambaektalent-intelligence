import json
import sqlite3
from neo4j import GraphDatabase
from openai import OpenAI
import time
import sys

sys.stdout.reconfigure(encoding='utf-8')

# OpenAI client initialization
with open("secrets.json", "r", encoding="utf-8") as f:
    secrets = json.load(f)

openai_client = OpenAI(api_key=secrets.get("OPENAI_API_KEY", ""))

# Connect to candidates.db and fetch careers
conn = sqlite3.connect('candidates.db')
cur = conn.cursor()
cur.execute("""
    SELECT id, name_kr, careers_json, profile_summary, sector
    FROM candidates
    WHERE is_duplicate=0
    AND careers_json IS NOT NULL
    AND length(careers_json) > 50
    LIMIT 500
""")
rows = cur.fetchall()
conn.close()

print(f"Loaded {len(rows)} candidates for career embeddings from candidates.db.")

def get_career_embedding(career: dict, candidate_info: dict) -> list:
    """단일 경력에 대한 임베딩 생성"""
    company = career.get('company', '')
    role = career.get('role', '') or career.get('title', '')
    duration = career.get('duration', '') or career.get('period', '')
    desc = career.get('description', '') or career.get('tasks', '')
    if isinstance(desc, list):
        desc = ' '.join(desc)
    
    text = f"{candidate_info['sector']} {company} {role} {duration} {desc[:500]}"
    
    resp = openai_client.embeddings.create(
        model="text-embedding-3-small",
        input=text[:2000]
    )
    return resp.data[0].embedding

# Neo4j setup
uri = secrets["NEO4J_URI"]
username = secrets["NEO4J_USERNAME"]
password = secrets["NEO4J_PASSWORD"]
driver = GraphDatabase.driver(uri, auth=(username, password))

processed = 0
for cid, name_kr, careers_json_str, summary, sector in rows:
    try:
        careers = json.loads(careers_json_str)
        if not isinstance(careers, list) or len(careers) == 0:
            continue
        
        cand_info = {'sector': sector or '', 'name': name_kr or ''}
        
        # 최근 3개 경력만 임베딩 (비용 절약)
        recent_careers = careers[:3]
        career_embeddings = []
        
        for career in recent_careers:
            emb = get_career_embedding(career, cand_info)
            career_embeddings.append(emb)
            time.sleep(0.01) # Avoid immediate rate limits
        
        # Serialize to JSON to avoid Neo4j nested collections limitation
        embeddings_json = json.dumps(career_embeddings)
        
        # Neo4j에 저장
        with driver.session() as s:
            s.run("""
                MATCH (c:Candidate {id: $cid})
                SET c.career_embeddings_json = $embeddings_json,
                    c.has_career_embeddings = true
            """, cid=cid, embeddings_json=embeddings_json)
        
        processed += 1
        if processed % 10 == 0:
            print(f'처리: {processed}명 / {len(rows)}')
            
    except Exception as e:
        print(f"Error on candidate {name_kr} ({cid}): {e}")
        continue

print(f'완료: {processed}명')
driver.close()
