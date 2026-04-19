
import json
import os
from connectors.pinecone_api import PineconeClient
from connectors.openai_api import OpenAIClient

def check_pinecone_metadata():
    secrets_path = "secrets.json"
    with open(secrets_path, "r") as f:
        secrets = json.load(f)
    
    pc_host = secrets.get("PINECONE_HOST", "")
    if pc_host and not pc_host.startswith("https://"):
        pc_host = f"https://{pc_host}"

    pinecone = PineconeClient(secrets["PINECONE_API_KEY"], pc_host)
    openai = OpenAIClient(secrets["OPENAI_API_KEY"])
    
    query_text = "Data Analyst Strategy KPI SQL Tableau"
    q_vec = openai.embed_content(query_text)
    if len(q_vec) > 768: q_vec = q_vec[:768]
        
    res = pinecone.query(q_vec, top_k=1, namespace="ns1")
    
    if res and "matches" in res and res['matches']:
        m = res['matches'][0]
        meta = m.get('metadata', {})
        print(f"Top Match ID: {m['id']}")
        print(f"Metadata Keys: {list(meta.keys())}")
        print("Metadata Content Sample:")
        # Print a few key fields to check language
        for k in ['name', 'position', 'experience_patterns', 'skill_score', 'canonical_role']:
            print(f"- {k}: {meta.get(k)}")
        
        # Check if patterns exist
        patterns = meta.get('experience_patterns', [])
        print(f"- experience_patterns (raw): {patterns}")
    else:
        print("No matches found.")

if __name__ == "__main__":
    check_pinecone_metadata()
