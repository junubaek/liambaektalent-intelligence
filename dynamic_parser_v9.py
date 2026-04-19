import os
import json
import time
import pdfplumber
import hashlib
import re
from docx import Document
from neo4j import GraphDatabase
import sqlite3
from datetime import datetime
from ontology_graph import CANONICAL_MAP

valid_nodes = set(CANONICAL_MAP.values())

from google import genai
from google.genai import types
from pydantic import BaseModel, Field
from enum import Enum
from typing import List
from tqdm import tqdm
from connectors.openai_api import OpenAIClient

with open("secrets.json", "r", encoding="utf-8") as f:
    secrets = json.load(f)
GEMINI_API_KEY = secrets["GEMINI_API_KEY"]

FOLDER1 = r"C:\Users\cazam\Downloads\02_resume 리스트 원본"
FOLDER2 = r"C:\Users\cazam\Downloads\02_resume_converted_docx"
FOLDER3 = r"C:\Users\cazam\Downloads\02_resume_converted_v8"
PROGRESS_FILE = r"C:\Users\cazam\Downloads\이력서자동분석검색시스템\processed_v9.json"

NEO4J_URI = "neo4j://127.0.0.1:7687"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "toss1234"

client = genai.Client(api_key=GEMINI_API_KEY)
MODEL_ID = "gemini-2.5-flash"
openai_client = OpenAIClient(secrets.get("OPENAI_API_KEY", ""))
driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))

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
    skills_used: list[SkillAction]

class CandidateChunks(BaseModel):
    candidate_name: str = Field(description="Must EXACTLY match the [FileName] provided in the prompt, including any underscores or spaces.")
    chunks: list[ExperienceChunkParsed] = Field(description="List of max 5 most recent role chunks spanning up to the last 7 years.")

class BatchChunkMap(BaseModel):
    results: list[CandidateChunks]

SYSTEM_PROMPT = """
You are an expert Headhunter AI parsing extreme tech standard resumes to graph database.
Extract up to the Top 5 most recent employment roles from the text (covering approx the last 5-7 years).
For each role (Chunk), extract the company name, role, dates, write a dense 2-sentence description of exactly what they built/managed, and list the SPECIFIC technical skills used there.
Assign one of the verb categories (BUILT, DESIGNED, MANAGED, etc.) to each skill.
"""

def extract_text(file_path):
    text = ""
    try:
        if file_path.endswith('.pdf'):
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    extracted = page.extract_text()
                    if extracted: text += extracted + "\n"
        elif file_path.endswith('.docx'):
            doc = Document(file_path)
            for para in doc.paragraphs:
                text += para.text + "\n"
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
    return text.strip()

def collect_files():
    files = {}
    for folder in [FOLDER1, FOLDER2, FOLDER3]:
        if not os.path.exists(folder): continue
        for sub_name in os.listdir(folder):
            sub_path = os.path.join(folder, sub_name)
            if os.path.isdir(sub_path):
                for f in os.listdir(sub_path):
                    if f.endswith('.pdf') or f.endswith('.docx'):
                        cand_name = os.path.splitext(f)[0]
                        files[cand_name] = os.path.join(sub_path, f)
            else:
                if sub_name.endswith('.pdf') or sub_name.endswith('.docx'):
                    cand_name = os.path.splitext(sub_name)[0]
                    files[cand_name] = sub_path
    return files

def parse_resume_batch(batch_dict: dict) -> dict:
    prompt = "Here are the resumes to parse into chunks (Format: [FileName]: [Resume Text]):\n\n"
    for filename, text in batch_dict.items():
        if len(text) > 8000: text = text[:8000]
        prompt += f"--- START [{filename}] ---\n{text}\n--- END [{filename}] ---\n\n"
        
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
            return {item.candidate_name: item.chunks for item in parsed.results}
    except Exception as e:
        print(f"Gemini API Error: {e}")
        time.sleep(5)
    return {}

def process_candidate_chunks(candidate_name, chunks, raw_text):
    if not chunks: return
    # Extract meta manually from filename
    name_kr = candidate_name.split()[0] if len(candidate_name.split()) > 0 else candidate_name
    document_hash = hashlib.sha256(raw_text.encode('utf-8')).hexdigest()
    
    with driver.session() as session:
        target_id = document_hash
        # Ensure Candidate exists
        session.run("""
            MERGE (c:Candidate {id: $id})
            SET c.name_kr = $name_kr
        """, id=target_id, name_kr=name_kr)
        
        # Build Chunks
        for i, chunk in enumerate(chunks):
            embed_text = f"Company: {chunk.company_name} Role: {chunk.role_name} Description: {chunk.description}"
            vec = openai_client.embed_content(embed_text)
            if not vec: continue
            
            chunk_id = hashlib.sha256(f"{target_id}_{chunk.company_name}_{i}".encode('utf-8')).hexdigest()
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
            """, cid=target_id, chunk_id=chunk_id, comp=chunk.company_name[:100], 
                 role=chunk.role_name[:100], start=chunk.start_date[:20], 
                 end=chunk.end_date[:20], desc=chunk.description[:1000], vec=vec)
            
            for sa in chunk.skills_used:
                skill = sa.skill
                if skill not in valid_nodes: continue
                action = getattr(sa, "action", "BUILT").upper()
                session.run(f"""
                    MATCH (e:Experience_Chunk {{id: $chunk_id}})
                    MERGE (s:Skill {{name: $skill}})
                    MERGE (e)-[r:{action}]->(s)
                    SET r.source = 'v9_parser', r.confidence = 1.0
                """, chunk_id=chunk_id, skill=skill)

def main():
    print("V9 Chunk-Level Native Parser Started")
    processed = {}
    if os.path.exists(PROGRESS_FILE):
        with open(PROGRESS_FILE, "r") as f:
            processed = json.load(f)
            
    files = collect_files()
    all_names = list(files.keys())
    
    batch_size = 3
    for i in tqdm(range(0, len(all_names), batch_size)):
        batch_names = all_names[i:i+batch_size]
        batch_dict = {}
        for name in batch_names:
            if name not in processed:
                batch_dict[name] = extract_text(files[name])
                
        if not batch_dict: continue
        
        parsed_results = parse_resume_batch(batch_dict)
        
        # Fuzzy match dict keys to avoid Gemini token normalization skips
        parsed_fuzzy = {k.lower().replace('_', ' ').replace(' ', ''): v for k, v in parsed_results.items()}
        
        for name, text in batch_dict.items():
            fuzzy_name = name.lower().replace('_', ' ').replace(' ', '')
            if fuzzy_name in parsed_fuzzy:
                chunks = parsed_fuzzy[fuzzy_name]
                process_candidate_chunks(name, chunks, text)
                processed[name] = {"text_hash": hashlib.md5(text.encode('utf-8')).hexdigest()}
        
        with open(PROGRESS_FILE, "w") as f:
            json.dump(processed, f)

if __name__ == "__main__":
    main()
