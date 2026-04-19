import os
import json
from ontology_graph import CANONICAL_MAP
from google import genai
from google.genai import types
from pydantic import BaseModel, Field
from enum import Enum

# Load API Key
with open("secrets.json", "r", encoding="utf-8") as f:
    secrets = json.load(f)
client = genai.Client(api_key=secrets["GEMINI_API_KEY"])
MODEL_ID = "gemini-2.5-flash"

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

FOLDER1 = r"C:\\Users\\cazam\\Downloads\\02_resume 리스트 원본"
FOLDER2 = r"C:\\Users\\cazam\\Downloads\\02_resume_converted_docx"
FOLDER3 = r"C:\\Users\\cazam\\Downloads\\02_resume_converted_v8"

def extract_text(file_path):
    import pdfplumber
    from docx import Document
    text = ""
    if file_path.endswith('.pdf'):
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                extracted = page.extract_text()
                if extracted: text += extracted + "\n"
    elif file_path.endswith('.docx'):
        doc = Document(file_path)
        for para in doc.paragraphs:
            text += para.text + "\n"
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

def run_test():
    files = collect_files()
    if not files:
        print("No files found.")
        return
        
    cand_name = list(files.keys())[0]
    sample_file = files[cand_name]
    print(f"Sample Candidate: {cand_name}")
    
    text = extract_text(sample_file)
    if len(text) > 8000: text = text[:8000]
    
    prompt = f"Here are the resumes to parse into chunks (Format: [FileName]: [Resume Text]):\n\n"
    prompt += f"--- START [{cand_name}] ---\n{text}\n--- END [{cand_name}] ---\n\n"
        
    config = types.GenerateContentConfig(
        response_mime_type="application/json",
        response_schema=BatchChunkMap,
        system_instruction=SYSTEM_PROMPT,
        temperature=0.1
    )
    
    print("\n[Requesting Gemini Parsing...]")
    response = client.models.generate_content(model=MODEL_ID, contents=prompt, config=config)
    parsed = response.parsed
    
    if not parsed or not parsed.results:
        print("Failed to parse.")
        return
        
    chunks = parsed.results[0].chunks
    print(f"\n[Parsed Success: {len(chunks)} chunks]")
    
    for c_idx, chunk in enumerate(chunks):
        print(f"\n--- Chunk {c_idx+1}: {chunk.company_name} | {chunk.role_name} ---")
        for sa in chunk.skills_used:
            raw_skill = sa.skill
            
            # TEST 1: The proposed fix (check if in CANONICAL_MAP keys)
            if raw_skill.lower() in {k.lower():v for k,v in CANONICAL_MAP.items()}:
                # Try to get casing right from the prompt or dictionary
                key_match = next((k for k in CANONICAL_MAP.keys() if k.lower() == raw_skill.lower()), None)
                canonical_val = CANONICAL_MAP[key_match]
                print(f"  [PASS] {raw_skill} -> {canonical_val}")
            
            # Or exactly in CANONICAL_MAP
            elif raw_skill in CANONICAL_MAP:
                print(f"  [PASS] {raw_skill} -> {CANONICAL_MAP[raw_skill]}")
                
            else:
                print(f"  [FAIL] {raw_skill} (Not in CANONICAL_MAP)")

if __name__ == '__main__':
    run_test()
