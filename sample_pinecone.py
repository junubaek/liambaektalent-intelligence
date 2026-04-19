
import json
import os
from connectors.pinecone_api import PineconeClient
from connectors.openai_api import OpenAIClient

def sample_candidates():
    secrets_path = "secrets.json"
    with open(secrets_path, "r") as f:
        secrets = json.load(f)
    
    pc_host = secrets.get("PINECONE_HOST", "")
    if pc_host and not pc_host.startswith("https://"):
        pc_host = f"https://{pc_host}"

    pinecone = PineconeClient(secrets["PINECONE_API_KEY"], pc_host)
    openai = OpenAIClient(secrets["OPENAI_API_KEY"])
    
    q_vec = [0.1] * 768 # Dummy vector
    res = pinecone.query(q_vec, top_k=50, namespace="ns1")
    
    has_patterns = 0
    has_skills = 0
    has_long_text = 0
    
    for m in res['matches']:
        meta = m.get('metadata', {})
        if meta.get('experience_patterns'): has_patterns += 1
        if meta.get('must_skills'): has_skills += 1
        # Check for any field longer than 100 chars
        if any(len(str(v)) > 100 for v in meta.values()): has_long_text += 1
            
    print(f"Sampled 50 candidates in ns1.")
    print(f"- Candidates with patterns: {has_patterns}")
    print(f"- Candidates with must_skills: {has_skills}")
    print(f"- Candidates with long text fields: {has_long_text}")

if __name__ == "__main__":
    sample_candidates()
