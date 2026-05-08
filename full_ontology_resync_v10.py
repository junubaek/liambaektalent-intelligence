import os
import json
import time
import hashlib
import sqlite3
from neo4j import GraphDatabase
from google import genai
from google.genai import types
from pydantic import BaseModel, Field
from enum import Enum
from typing import List
from tqdm import tqdm
from connectors.openai_api import OpenAIClient
from ontology_graph import CANONICAL_MAP

# 1. Configuration
with open("secrets.json", "r", encoding="utf-8") as f:
    secrets = json.load(f)

GEMINI_API_KEY = secrets["GEMINI_API_KEY"]
NEO4J_URI = secrets.get("NEO4J_URI", "neo4j://127.0.0.1:7687")
NEO4J_USER = secrets.get("NEO4J_USERNAME", "neo4j")
NEO4J_PASSWORD = secrets.get("NEO4J_PASSWORD", "toss1234")

client = genai.Client(api_key=GEMINI_API_KEY)
MODEL_ID = "gemini-flash-latest"
openai_client = OpenAIClient(secrets.get("OPENAI_API_KEY", ""))
driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
valid_nodes = set(CANONICAL_MAP.values())

# 2. Models
class ActionEnum(str, Enum):
    BUILT = "BUILT"
    DESIGNED = "DESIGNED"
    MANAGED = "MANAGED"
    ANALYZED = "ANALYZED"
    LAUNCHED = "LAUNCHED"
    NEGOTIATED = "NEGOTIATED"
    GREW = "GREW"
    SUPPORTED = "SUPPORTED"
    MIGRATED = "MIGRATED"
    DEPLOYED = "DEPLOYED"
    RESOLVED = "RESOLVED"
    CLOSED = "CLOSED"
    DRAFTED = "DRAFTED"

class SkillAction(BaseModel):
    skill: str = Field(description="Only use standard IT/Business skill nouns")
    action: ActionEnum

class ExperienceChunkParsed(BaseModel):
    company_name: str
    role_name: str
    start_date: str
    end_date: str
    description: str = Field(description="Dense 2-sentence summary of technical achievements at this company.")
    skills_used: List[SkillAction]

class CandidateChunks(BaseModel):
    candidate_id: str = Field(description="Must EXACTLY match the [CandidateID] provided in the prompt.")
    chunks: List[ExperienceChunkParsed]

class BatchChunkMap(BaseModel):
    results: List[CandidateChunks]

SYSTEM_PROMPT = """
You are an expert Headhunter AI parsing extreme tech standard resumes to graph database.
Extract up to the Top 5 most recent employment roles from the text (covering approx the last 5-7 years).
For each role (Chunk), extract the company name, role, dates, write a dense 2-sentence description of exactly what they built/managed, and list the SPECIFIC technical skills used there.
Assign one of the verb categories (BUILT, DESIGNED, MANAGED, etc.) to each skill.
"""

# 3. Logic
def parse_resume_batch(batch_dict: dict) -> dict:
    prompt = "Here are the resumes to parse into chunks (Format: [CandidateID]: [Resume Text]):\n\n"
    for cid, text in batch_dict.items():
        if len(text) > 8000: text = text[:8000]
        prompt += f"--- START [{cid}] ---\n{text}\n--- END [{cid}] ---\n\n"
        
    config = types.GenerateContentConfig(
        response_mime_type="application/json",
        response_schema=BatchChunkMap,
        system_instruction=SYSTEM_PROMPT,
        temperature=0.1
    )
    
    try:
        response = client.models.generate_content(model=MODEL_ID, contents=prompt, config=config)
        parsed = response.parsed
        if parsed and parsed.results:
            return {item.candidate_id: item.chunks for item in parsed.results}
    except Exception as e:
        print(f"Gemini API Error: {e}")
        time.sleep(5)
    return {}

def process_candidate_chunks(cid, name_kr, chunks, i):
    if not chunks: return
    
    with driver.session() as session:
        # 4. Canonical normalization (Keys and Values)
        # Map both lowercased keys and lowercased values to the canonical value
        valid_lower_map = {k.lower().strip(): v for k, v in CANONICAL_MAP.items()}
        valid_lower_map.update({v.lower().strip(): v for v in CANONICAL_MAP.values()})

        # 5. Build Chunks
        for i, chunk in enumerate(chunks):
            embed_text = f"Company: {chunk.company_name} Role: {chunk.role_name} Description: {chunk.description}"
            vec = openai_client.embed_content(embed_text)
            if not vec: continue
            
            chunk_id = hashlib.sha256(f"{cid}_{chunk.company_name}_{i}".encode('utf-8')).hexdigest()
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
            """, cid=cid, chunk_id=chunk_id, comp=chunk.company_name[:100], 
                 role=chunk.role_name[:100], start=chunk.start_date[:20], 
                 end=chunk.end_date[:20], desc=chunk.description[:1000], vec=vec)
            
            for sa in chunk.skills_used:
                skill_raw = sa.skill
                # Fuzzy match: try exact, then try normalized
                skill_norm = skill_raw.lower().replace('_', ' ').strip()
                skill_norm_underscore = skill_raw.lower().replace(' ', '_').strip()
                
                if skill_raw in valid_nodes: # Direct match with value
                    skill_canonical = skill_raw
                elif skill_norm in valid_lower_map:
                    skill_canonical = valid_lower_map[skill_norm]
                elif skill_norm_underscore in valid_lower_map:
                    skill_canonical = valid_lower_map[skill_norm_underscore]
                else:
                    print(f"  [Skill Filtered] {skill_raw} is not in canonical map.", flush=True)
                    continue
                
                action = getattr(sa, "action", "BUILT").upper()
                session.run(f"""
                    MATCH (e:Experience_Chunk {{id: $chunk_id}})
                    MERGE (s:Skill {{name: $skill}})
                    MERGE (e)-[r:{action}]->(s)
                    SET r.source = 'v10_resync', r.confidence = 1.0
                """, chunk_id=chunk_id, skill=skill_canonical)

BATCH_SIZE = 10
PROCESSED_FILE = "processed_resync_v10.json"

def load_processed():
    if os.path.exists(PROCESSED_FILE):
        with open(PROCESSED_FILE, 'r') as f:
            return set(json.load(f))
    return set()

def save_processed(processed_set):
    with open(PROCESSED_FILE, 'w') as f:
        json.dump(list(processed_set), f)

def main():
    print("V10 Full Ontology Resync Started (Optimized Batch & Resume)")
    
    with open('resync_no_skills.json', 'r') as f:
        target_ids = json.load(f)
    
    processed_ids = load_processed()
    remaining_targets = [tid for tid in target_ids if tid not in processed_ids]
    
    print(f"Total targets: {len(target_ids)}")
    print(f"Already processed: {len(processed_ids)}")
    print(f"Remaining: {len(remaining_targets)}")
    
    conn = sqlite3.connect('candidates.db')
    cur = conn.cursor()
    
    for i in tqdm(range(0, len(remaining_targets), BATCH_SIZE)):
        batch_ids = remaining_targets[i:i+BATCH_SIZE]
        
        # Get data from SQLite (using resume_text or raw_text)
        placeholders = ','.join(['?'] * len(batch_ids))
        # Checking which column exists: resume_text vs raw_text. I'll use raw_text based on view_file output.
        cur.execute(f"SELECT id, name_kr, raw_text FROM candidates WHERE id IN ({placeholders})", batch_ids)
        rows = cur.fetchall()
        
        batch_dict = {row[0]: row[2] for row in rows if row[2]}
        name_map = {row[0]: row[1] for row in rows}
        
        if not batch_dict: 
            for tid in batch_ids: processed_ids.add(tid)
            save_processed(processed_ids)
            continue
        
        parsed_results = parse_resume_batch(batch_dict)
        print(f"  [Debug] Received results from Gemini. Keys: {list(parsed_results.keys())}", flush=True)
        
        parsed_fuzzy = {k.lower().strip(): v for k, v in parsed_results.items()}
        
        for idx, cid in enumerate(batch_ids):
            fuzzy_cid = cid.lower().strip()
            if fuzzy_cid in parsed_fuzzy:
                chunks = parsed_fuzzy[fuzzy_cid]
                print(f"  [Match Success] Processing {name_map.get(cid)} ({cid}) - {len(chunks)} chunks found.", flush=True)
                process_candidate_chunks(cid, name_map.get(cid, "Unknown"), chunks, idx)
            else:
                print(f"  [Match Failed] No results for {name_map.get(cid)} ({cid}) in Gemini response.", flush=True)
            
            processed_ids.add(cid)
        
        save_processed(processed_ids)
        time.sleep(1)
            
    conn.close()
    driver.close()
    print("\n--- V10 Resync Complete ---")

if __name__ == "__main__":
    main()
