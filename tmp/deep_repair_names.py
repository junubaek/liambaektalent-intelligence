import sqlite3
import os
import json
import time
from dotenv import load_dotenv
load_dotenv()

from google import genai
from google.genai import types
from neo4j import GraphDatabase

conn = sqlite3.connect('candidates.db')
cursor = conn.cursor()

cursor.execute("SELECT id, name_kr, raw_text FROM candidates")
rows = cursor.fetchall()

job_keywords = ["자금", "재무", "회계", "HR", "인사", "마케팅", "영업", "Sales", "기획", 
               "개발", "디자인", "MD", "상품", "전략", "PR", "총무", "품질", "오퍼레이션", "경영"]

bad_records = []
for row in rows:
    c_id, name_kr, raw_text = row
    if not name_kr:
        continue
    is_suspect = False
    for word in job_keywords:
        if word in name_kr and len(name_kr) <= 6 and not name_kr.endswith("님") and name_kr not in ["권기획", "이경영", "김경영", "박영업", "최디자인", "이영업"]:
            if name_kr == word or name_kr == f"{word}담당" or name_kr == f"{word}팀장" or "전문가" in name_kr:
                is_suspect = True
            elif len(name_kr) < 5 and word in name_kr:
                is_suspect = True
    if is_suspect:
        bad_records.append({"id": c_id, "old_name": name_kr, "raw_text": raw_text})

print(f"Targeting {len(bad_records)} records for Deep Repair via Gemini...")

secrets_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "secrets.json")
with open(secrets_path, "r", encoding="utf-8") as f:
    secrets = json.load(f)

client = genai.Client(api_key=secrets["GEMINI_API_KEY"])
neo4j_driver = GraphDatabase.driver("bolt://127.0.0.1:7687", auth=("neo4j", "toss1234"))

success_count = 0

for i, record in enumerate(bad_records):
    c_id = record['id']
    old_name = record['old_name']
    text = record['raw_text']
    
    if not text:
        continue
        
    prompt = f"""
다음은 지원자 이력서의 원문 텍스트입니다.
1. 이력서에서 지원자의 '진짜 한국어 성명(보통 2~4글자)'만 추출하세요. 
2. 직무명(예: 재무회계, 자금, 기획, 기획팀 등), '이력서', 지원분야, 회사명 등의 단어는 절대 포함하지 마세요.
3. 이름을 도저히 확실하게 찾을 수 없다면 '미상'이라고만 출력하세요.
4. 오직 이름만 답변하세요.

[이력서 텍스트]
{text[:2500]}
"""
    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash-lite',
            contents=prompt,
        )
        new_name = response.text.strip().replace(" ", "").replace("성명:", "").replace("이름:", "").strip()
        
        if len(new_name) > 6 or new_name in job_keywords or "팀" in new_name or "회계" in new_name or "기획" in new_name:
            new_name = "미상"
            
        print(f"[{i+1}/{len(bad_records)}] {old_name} -> {new_name}")
        
        cursor.execute("UPDATE candidates SET name_kr = ? WHERE id = ?", (new_name, c_id))
        
        with neo4j_driver.session() as session:
            session.run("""
                MATCH (c:Candidate {id: $cid})
                SET c.name_kr = $nname, c.name = $nname
            """, cid=c_id, nname=new_name)
            
        success_count += 1
        time.sleep(1) # Rate limit protection
            
    except Exception as e:
        print(f"Error repairing {c_id} ({old_name}): {e}")
        time.sleep(5)

conn.commit()
conn.close()
neo4j_driver.close()

print(f"\n✅ 딥 리페어 완료: {success_count}명의 이름을 복구하고 SQLite와 Neo4j에 동기화했습니다.")
