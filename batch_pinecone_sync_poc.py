import os
import json
import time
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models import Candidate
from openai import OpenAI
from connectors.pinecone_api import PineconeClient

# Setup
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
        return text + f"\n[Keywords: {', '.join(list(found))}]"
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
                "metadata": {"candidate_id": candidate.id, "chunk_index": i}
            })
            
        res = pinecone_client.upsert(vectors_to_upsert, namespace="resume_vectors")
        if res:
            candidate.is_pinecone_synced = True
            db.commit()
            return True
        return False
    except Exception as e:
        print(f"Error {candidate.name_kr}: {e}")
        return False
        
def main():
    db = SessionLocal()
    target_names = ['남연우', '백인호', '조현우', '이민찬', '정태현', '김완희', '김상엽', '이기준', '박우람', '신종수']
    
    try:
        cands = db.query(Candidate).filter(Candidate.name_kr.in_(target_names), Candidate.is_duplicate==0).all()
        print(f"Found {len(cands)} candidates for POC.")
        for c in cands:
            print(f"Re-embedding {c.name_kr}...")
            sync_candidate_to_pinecone(c, db)
            time.sleep(0.3)
    finally:
        db.close()
        
    print("POC complete.")

if __name__ == "__main__":
    main()
