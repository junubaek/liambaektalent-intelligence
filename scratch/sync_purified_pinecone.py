import sqlite3
import json
import time
import os
import sys

sys.path.append(r"C:\Users\cazam\Downloads\이력서자동분석검색시스템")
sys.stdout.reconfigure(encoding='utf-8')
from openai import OpenAI

# secrets.json에서 키 및 호스트 정보 로드
secrets_path = r"C:\Users\cazam\Downloads\이력서자동분석검색시스템\secrets.json"
with open(secrets_path, "r", encoding="utf-8") as f:
    secrets = json.load(f)

openai_client = OpenAI(api_key=secrets.get("OPENAI_API_KEY", ""))
host = secrets.get("PINECONE_HOST", "").rstrip("/")
if not host.startswith("https://"):
    host = f"https://{host}"

from connectors.pinecone_api import PineconeClient
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

db_path = r"C:\Users\cazam\Downloads\이력서자동분석검색시스템\candidates.db"
conn = sqlite3.connect(db_path)
conn.row_factory = sqlite3.Row
cur = conn.cursor()

# Pinecone 동기화 안 된 활성(중복아닌) 후보자 조회
cur.execute("""
    SELECT id, name_kr, raw_text, sector 
    FROM candidates 
    WHERE is_duplicate = 0 
      AND (is_pinecone_synced = 0 OR is_pinecone_synced IS NULL)
      AND raw_text IS NOT NULL 
      AND length(raw_text) > 100
""")
rows = cur.fetchall()

print(f"Total unsynced candidates found: {len(rows)}")

success = 0
for idx, r in enumerate(rows, 1):
    cid, name_kr, raw_text, sector = r['id'], r['name_kr'], r['raw_text'], r['sector']
    chunks = chunk_text(raw_text)
    if not chunks:
        continue
    
    print(f"[{idx}/{len(rows)}] Syncing {name_kr} ({cid}) -> {len(chunks)} chunks...")
    try:
        response = openai_client.embeddings.create(model="text-embedding-3-small", input=chunks)
        vectors_to_upsert = []
        for i, emb_data in enumerate(response.data):
            vectors_to_upsert.append({
                "id": f"{cid}_chunk_{i}",
                "values": emb_data.embedding,
                "metadata": {"candidate_id": str(cid), "chunk_index": i}
            })
            
        res = pinecone_client.upsert(vectors_to_upsert, namespace="resume_vectors")
        if res:
            cur.execute("UPDATE candidates SET is_pinecone_synced = 1 WHERE id = ?", (cid,))
            conn.commit()
            success += 1
            print(f"  Success: {name_kr}")
        else:
            print(f"  Failed Pinecone upload for {name_kr}")
        
        time.sleep(0.05) # Rate limit 방지
    except Exception as e:
        print(f"  Error syncing {name_kr}: {e}")

conn.close()
print(f"\nPinecone Sync Complete! Successfully synced {success}/{len(rows)} candidates.")
