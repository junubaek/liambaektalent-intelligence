import os
import json
import sqlite3
import time
import hashlib
from concurrent.futures import ThreadPoolExecutor, as_completed
from neo4j import GraphDatabase
from google import genai
from google.genai import types
from pydantic import BaseModel, Field
from connectors.openai_api import OpenAIClient

def load_secrets():
    with open("secrets.json", "r", encoding="utf-8") as f:
        return json.load(f)

# Pydantic schema for Gemini Structuring
class SkillAction(BaseModel):
    skill: str
    action: str

class ExperienceChunkParsed(BaseModel):
    company_name: str
    role_name: str
    start_date: str
    end_date: str
    description: str
    skills_used: list[SkillAction]

class ChunkPartitionResult(BaseModel):
    chunks: list[ExperienceChunkParsed]

SYSTEM_PROMPT = """
You are an expert Headhunter AI. You are given a Candidate's raw resume text, their core career timeline (max 3 recent companies), and a list of Technical Skills with Actions that have already been extracted from this resume.
Your job is to partition these skills into the specific company (Experience_Chunk) where they were utilized, based on the text.
If a skill is clearly used at Company A, put it under Company A's skills_used field. If the timeline is unclear, put it in the most recent relevant chunk.
Also, write a dense 2-sentence summary 'description' of what the candidate technically accomplished at that company.
IMPORTANT: You must preserve the EXACT 'skill' and 'action' string format provided in the input list. Do not alter skill names.
"""

def process_candidate(cand_data, gemini_client, openai_client, neo4j_driver):
    # cand_data: {"name_kr": ..., "hash": ..., "raw_text": ..., "careers": [...], "skills": [{"skill": "Python", "action": "BUILT"}...]}
    if not cand_data["careers"]: return False
    
    # Sort and slice top 3 recent careers
    try:
        careers = json.loads(cand_data["careers"])
        # Assume usually reverse chronological or just take first 3 if it's typical layout
        # (A robust sort could parse standard dates, but let's take first 3 for simplicity)
        recent_careers = careers[:3] 
    except:
        recent_careers = [{"company": "Unknown", "title": "Professional", "start_date": "", "end_date": "현재"}]

    prompt = f"Candidate Careers: {json.dumps(recent_careers, ensure_ascii=False)}\n\n"
    prompt += f"System Extracted Skills: {json.dumps(cand_data['skills'], ensure_ascii=False)}\n\n"
    prompt += f"Raw Resume Text Snippet:\n{cand_data['raw_text'][:4000]}"

    config = types.GenerateContentConfig(
        response_mime_type="application/json",
        response_schema=ChunkPartitionResult,
        system_instruction=SYSTEM_PROMPT,
        temperature=0.1
    )

    try:
        res = gemini_client.models.generate_content(model="gemini-2.5-flash", contents=prompt, config=config)
        parsed = res.parsed
        if not parsed or not parsed.chunks: return False
        
        with neo4j_driver.session() as session:
            # 1. DELETE existing direct skill edges from Candidate to avoid duplication
            session.run("MATCH (c:Candidate {id: $id})-[r]->(s:Skill) DELETE r", id=cand_data["hash"])
            
            # 2. Iterate created chunks
            for i, chunk in enumerate(parsed.chunks):
                # Embed the detailed description + company meta context
                embed_text = f"Company: {chunk.company_name} Role: {chunk.role_name} Description: {chunk.description}"
                vec = openai_client.embed_content(embed_text)
                if not vec: continue
                
                chunk_id = hashlib.sha256(f"{cand_data['hash']}_{chunk.company_name}_{i}".encode('utf-8')).hexdigest()
                
                # Create Chunk Node & Link to Candidate
                session.run("""
                    MATCH (c:Candidate {id: $cid})
                    MERGE (e:Experience_Chunk {id: $chunk_id})
                    SET e.company_name = $comp,
                        e.role_name = $role,
                        e.start_date = $start,
                        e.end_date = $end,
                        e.description = $desc,
                        e.embedding = $vec
                    MERGE (c)-[:HAS_EXPERIENCE]->(e)
                """, cid=cand_data["hash"], chunk_id=chunk_id, comp=chunk.company_name, 
                     role=chunk.role_name, start=chunk.start_date, end=chunk.end_date, desc=chunk.description, vec=vec)
                
                # Re-attach specific skills to this chunk
                for sa in chunk.skills_used:
                    session.run(f"""
                        MATCH (e:Experience_Chunk {{id: $chunk_id}})
                        MERGE (s:Skill {{name: $skill}})
                        MERGE (e)-[r:{sa.action}]->(s)
                    """, chunk_id=chunk_id, skill=sa.skill)
        return True
    except Exception as e:
        print(f"Error processing {cand_data['name_kr']}: {e}")
        return False

def run_targeted_migration(target_name_keyword=None, limit=50):
    secrets = load_secrets()
    gemini = genai.Client(api_key=secrets["GEMINI_API_KEY"])
    openai = OpenAIClient(secrets["OPENAI_API_KEY"])
    driver = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "toss1234"))
    
    # Pre-fetch existing Neo4j edges to carry over
    neo4j_skills = {}
    with driver.session() as s:
        res = s.run("MATCH (c:Candidate)-[r]->(s:Skill) RETURN c.id AS cid, type(r) AS action, s.name AS skill")
        for record in res:
            cid = record["cid"]
            if cid not in neo4j_skills: neo4j_skills[cid] = []
            neo4j_skills[cid].append({"skill": record["skill"], "action": record["action"]})
            
    conn = sqlite3.connect("candidates.db")
    c = conn.cursor()
    query = "SELECT name_kr, document_hash, raw_text, careers_json FROM candidates WHERE raw_text IS NOT NULL AND careers_json IS NOT NULL"
    if target_name_keyword:
        query += f" AND (raw_text LIKE '%{target_name_keyword}%')"
    query += f" LIMIT {limit}"
    
    c.execute(query)
    rows = c.fetchall()
    conn.close()
    
    valid_cands = []
    for r in rows:
        cid = r[1]
        if cid in neo4j_skills:
            valid_cands.append({
                "name_kr": r[0],
                "hash": cid,
                "raw_text": r[2],
                "careers": r[3],
                "skills": neo4j_skills[cid]
            })
            
    print(f"Starting chunk migration for {len(valid_cands)} targeted candidates...")
    success = 0
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = {executor.submit(process_candidate, c, gemini, openai, driver): c for c in valid_cands}
        for future in as_completed(futures):
            if future.result(): success += 1
            print(f"Processed: {success}/{len(valid_cands)}")
            
    driver.close()
    print("Migration batch complete.")

if __name__ == "__main__":
    import sys
    keyword = sys.argv[1] if len(sys.argv) > 1 else None
    run_targeted_migration(keyword, 50)
