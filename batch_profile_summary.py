import sqlite3
import os
import json
import asyncio
import time
from neo4j import GraphDatabase
from jd_compiler import client as genai_client
from google.genai import types

DB_FILE = "candidates.db"

# Prompt requested
# "아래 이력서를 보고 이 사람이 누구인지 한 문장으로 요약해줘.
# 형식: N년 경력의 [핵심역량] 전문가로 [주요 회사/경험]을 보유하고 있습니다.
# 반드시 한국어 1문장만 출력"

SYSTEM_PROMPT = """아래 이력서를 보고 이 사람이 누구인지 한 문장으로 요약해줘.
형식: N년 경력의 [핵심역량] 전문가로 [주요 회사/경험]을 보유하고 있습니다.
반드시 한국어 1문장만 출력"""

async def generate_profile_summary(text: str) -> str:
    if not text or len(text) < 10:
        return ""
        
    config = types.GenerateContentConfig(
        system_instruction=SYSTEM_PROMPT,
        temperature=0.1
    )
    
    try:
        # Using 2.5-flash-lite as it's the valid available model replacing 2.0-flash-lite
        response = await genai_client.aio.models.generate_content(
            model="gemini-2.5-flash-lite",
            contents=[f'이력서 텍스트: "{text[:1500]}"'],
            config=config
        )
        return response.text.strip().replace('\n', ' ')
    except Exception as e:
        print(f"API Error: {e}")
        return ""

async def main():
    print("🚀 Starting Profile Summary Batch Generation (V8.5 ORM)...")
    
    from app.database import SessionLocal
    from app.models import Candidate, ParsingCache
    
    db = SessionLocal()
    
    # Select candidates where ParsingCache does not have a profile_summary
    rows = db.query(Candidate).join(ParsingCache).all()
    targets = []
    for c in rows:
        cache_dict = c.parsing_cache.parsed_dict
        if not cache_dict.get("profile_summary"):
            targets.append((c.id, c.name_kr, c.raw_text, c.parsing_cache))
            
    print(f"📋 Found {len(targets)} candidates needing summary.")
    
    # Load secrets
    secrets_path = os.path.join(os.path.dirname(__file__), "secrets.json")
    with open(secrets_path, "r", encoding="utf-8") as f:
        secrets = json.load(f)
    
    neo4j_pwd = secrets.get('NEO4J_PASSWORD', 'toss1234')
    driver = GraphDatabase.driver('bolt://localhost:7687', auth=('neo4j', neo4j_pwd))
    
    success = 0
    fail = 0
    
    with driver.session() as session:
        for i, (cid, name_kr, raw_text, p_cache) in enumerate(targets):
            print(f"[{i+1}/{len(targets)}] Generating for {name_kr}...")
            
            if not raw_text:
                print(f"  -> ⚠️ No text available for {name_kr}, skipping.")
                fail += 1
                continue
                
            # Grab first 1500 chars to save money/latency
            res_summary = await generate_profile_summary(raw_text[:1500])
            
            if res_summary:
                # Update SQLite SQLAlchemy JSON Object
                cache_dict = p_cache.parsed_dict
                cache_dict["profile_summary"] = res_summary
                p_cache.parsed_dict = cache_dict
                
                # Update Neo4j
                session.run("MATCH (c:Candidate {id: $id}) SET c.profile_summary = $val", {"id": cid, "val": res_summary})
                
                success += 1
                print(f"  -> ✅ {res_summary}")
                
                # Auto-save every 10
                if success % 10 == 0:
                    db.commit()
                    print(f"  💾 Auto-saved 10 records.")
            else:
                fail += 1
                
            await asyncio.sleep(0.5)
            
    db.commit()
    db.close()
    driver.close()
    
    print(f"\n✨ Batch Generation Complete! Success: {success}, Failed: {fail}")

if __name__ == "__main__":
    asyncio.run(main())
