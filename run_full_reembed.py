import os
import json
import time
from sqlalchemy import text
from app.database import SessionLocal
from connectors.pinecone_api import PineconeClient
import requests
import subprocess
import sys

sys.stdout.reconfigure(encoding='utf-8')

# Setup
with open("secrets.json", "r", encoding="utf-8") as f:
    secrets = json.load(f)

pinecone_key = secrets.get("PINECONE_API_KEY", "")
host = secrets.get("PINECONE_HOST", "").rstrip("/")
if not host.startswith("https://"):
    host = f"https://{host}"

# 1. Clear Pinecone Namespace
print("Clearing Pinecone vectors in 'resume_vectors'...")
try:
    resp = requests.post(
        f"{host}/vectors/delete", 
        headers={"Api-Key": pinecone_key, "Content-Type": "application/json"},
        json={"deleteAll": True, "namespace": "resume_vectors"}
    )
    if resp.status_code == 200:
        print("Pinecone namespace cleared successfully.")
    else:
        print(f"Failed to clear namespace: {resp.text}")
except Exception as e:
    print(f"Error clearing Pinecone: {e}")

# Wait to ensure deletion propagates
time.sleep(5)

# 2. Reset SQLite status
db = SessionLocal()
try:
    db.execute(text("UPDATE candidates SET is_pinecone_synced = 0"))
    db.commit()
    print("SQLite synced status reset.")
except Exception as e:
    print(f"SQLite reset error: {e}")
finally:
    db.close()

# 3. Write target logic
poc_code = """import os
import json
import time
import sys
sys.stdout.reconfigure(encoding='utf-8')
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models import Candidate
from openai import OpenAI
from connectors.pinecone_api import PineconeClient

with open("secrets.json", "r") as f:
    secrets = json.load(f)

openai_client = OpenAI(api_key=secrets.get("OPENAI_API_KEY", ""))
host = secrets.get("PINECONE_HOST", "").rstrip("/")
if not host.startswith("https://"):
    host = f"https://{host}"
pinecone_client = PineconeClient(secrets.get("PINECONE_API_KEY", ""), host)

HIDDEN_MAP = {
    "상장": ["IPO", "IPO_Preparation"],
    "기업공개": ["IPO", "IPO_Preparation"],
    "투자자": ["Investor_Relations", "IR"],
    "기업설명회": ["Investor_Relations", "IR"],
    "반도체 설계": ["RTL_Design", "Circuit_Design"],
    "시스템반도체": ["System_on_Chip", "SoC"],
    "테스트 설계": ["Design_for_Testability", "DFT"],
    "재무모델": ["Financial_Modeling"],
    "재무모델링": ["Financial_Modeling"],
    "데이터시각화": ["Tableau", "Data_Visualization"],
    "시각화": ["Tableau", "Data_Visualization"],
    "클라우드 서비스": ["SaaS", "Cloud_Computing"],
    "물류 자동화": ["ASRS", "Warehouse_Automation"],
    "자동창고": ["ASRS", "Warehouse_Automation"],
    "ERP 시스템": ["SAP_ERP", "ERP"],
    "영업 자동화": ["DevOps", "CI_CD"],
    "앱 개발": ["Kotlin", "Android_Development"],
    "안드로이드": ["Kotlin", "Android_Development"]
}

def inject_hidden_keywords(text: str) -> str:
    found = set()
    for ko_word, en_tags in HIDDEN_MAP.items():
        if ko_word in text:
            found.update(en_tags)
    if found:
        return text + f"\\n[Keywords: {', '.join(list(found))}]"
    return text

def chunk_text(text: str, chunk_size: int = 1000):
    if not text: return []
    chunks = [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]
    return [inject_hidden_keywords(c) for c in chunks]

def sync_candidate_to_pinecone(candidate: Candidate, db: Session):
    chunks = chunk_text(candidate.raw_text)
    if not chunks: return True
        
    try:
        response = openai_client.embeddings.create(model="text-embedding-3-small", input=chunks)
        vectors_to_upsert = []
        for i, emb_data in enumerate(response.data):
            vectors_to_upsert.append({
                "id": f"{candidate.id}_chunk_{i}",
                "values": emb_data.embedding,
                "metadata": {"candidate_id": str(candidate.id), "chunk_index": i}
            })
            
        res = pinecone_client.upsert(vectors_to_upsert, namespace="resume_vectors")
        if res:
            candidate.is_pinecone_synced = True
            db.commit()
            return True
        return False
    except Exception as e:
        print(f"Error {candidate.id}: {e}")
        return False

def main():
    print("Starting Bulk Hidden Keyword Re-embedding...")
    db = SessionLocal()
    success = 0
    try:
        targets = db.query(Candidate).filter(Candidate.is_pinecone_synced == False, Candidate.is_duplicate == 0).all()
        total = len(targets)
        print(f"Total targets: {total}")
        for i, c in enumerate(targets):
            if i % 100 == 0:
                print(f"Progress: {i}/{total}")
            if sync_candidate_to_pinecone(c, db):
                success += 1
            # Add small delay to prevent rate limits
            time.sleep(0.05)
    finally:
        db.close()
    print(f"Complete: {success}/{total}")

if __name__ == '__main__':
    main()
"""

with open("batch_pinecone_sync.py", "w", encoding="utf-8") as f:
    f.write(poc_code)
    
print("Updated batch_pinecone_sync.py logic.")

# 4. Now run it
print("Running sync...")
subprocess.run(["python", "-X", "utf8", "batch_pinecone_sync.py"], check=True)

# 5. Run tests
print("=============================")
print("Running NDCG benchmark...")
subprocess.run(["python", "-X", "utf8", "test_ndcg_v8.py"])

print("=============================")
print("Running Auditor...")
subprocess.run(["python", "-X", "utf8", "system_auditor.py"])
