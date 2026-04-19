import sys
import os
import json
import sqlite3
import time
import subprocess
from datetime import datetime

sys.stdout.reconfigure(encoding='utf-8')
os.chdir(r"c:\Users\cazam\Downloads\이력서자동분석검색시스템")
sys.path.append(os.getcwd())

with open("secrets.json", "r", encoding="utf-8") as f:
    secrets = json.load(f)

# 1. Pinecone Delete All
try:
    from connectors.pinecone_api import PineconeClient
    host = secrets.get("PINECONE_HOST", "").rstrip("/")
    if not host.startswith("https://"): host = f"https://{host}"
    pc = PineconeClient(secrets.get("PINECONE_API_KEY", ""), host)

    print(f"[{datetime.now().strftime('%H:%M:%S')}] [1] Deleting all vectors in 'resume_vectors'...")
    res = pc.delete(delete_all=True, namespace="resume_vectors")
    print(f"Delete Response: {res}")
    time.sleep(3)
except Exception as e:
    print(f"Pinecone Delete Failed: {e}")

# 2. Reset DB sync status
try:
    print(f"\n[{datetime.now().strftime('%H:%M:%S')}] [2] Resetting SQLite is_pinecone_synced = 0 ...")
    db_path = "candidates.db"
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("UPDATE candidates SET is_pinecone_synced = 0 WHERE is_duplicate=0 AND is_parsed=1")
    conn.commit()
    print(f"Updated {cur.rowcount} rows to is_pinecone_synced=0.")
    conn.close()
except Exception as e:
    print(f"DB Update Failed: {e}")

# 3. Run batch_pinecone_sync.py
try:
    print(f"\n[{datetime.now().strftime('%H:%M:%S')}] [3] Running batch_pinecone_sync.py (Expected time: 10-15 mins)...")
    sys.stdout.flush()
    # Execute batch_pinecone_sync synchronously
    sub = subprocess.run(["python", "-X", "utf8", "batch_pinecone_sync.py"], capture_output=True, text=True, encoding="utf-8")
    
    # Print the last 1000 characters of stdout to see the summary "Success: X/Y"
    print(sub.stdout[-1000:])
    print("batch_pinecone_sync.py completed with code", sub.returncode)
except Exception as e:
    print(f"Sync Script Failed: {e}")

# 4. Verification Check
try:
    print(f"\n[{datetime.now().strftime('%H:%M:%S')}] [4] Verification Check ...")
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("SELECT count(*) FROM candidates WHERE is_duplicate=0 AND is_parsed=1 AND is_pinecone_synced=1")
    synced = cur.fetchone()[0]
    print(f"Total synced successfully in DB: {synced}")
    conn.close()

    dummy_vec = [0.01] * 1536
    res = pc.query(dummy_vec, top_k=3, namespace="resume_vectors")
    if res and "matches" in res:
        for idx, match in enumerate(res["matches"]):
            print(f"Sample {idx+1} ID: {match.get('id')}")
            print(f"Metadata: {match.get('metadata')}")
except Exception as e:
    print(f"Verification Failed: {e}")

# 5. Run test_ndcg_v8.py
try:
    print(f"\n[{datetime.now().strftime('%H:%M:%S')}] [5] Running test_ndcg_v8.py to measure V9 chunking performance...")
    sys.stdout.flush()
    sub2 = subprocess.run(["python", "-X", "utf8", "test_ndcg_v8.py"], capture_output=True, text=True, encoding="utf-8")
    for line in sub2.stdout.split('\n'):
        if "결과 리포트" in line or "현재 측정값" in line or "변화율" in line or "완벽 검색" in line or "최고 성능 쿼리" in line or "최저 성능" in line or "이전 베이스라인" in line:
            print(line)
        if line.startswith("최저 성능") or line.startswith("최고 성능"):
            print(line)
            
    # Print the last chunk of report
    print(sub2.stdout[-600:])
except Exception as e:
    print(f"NDCG Error: {e}")

print(f"\n[{datetime.now().strftime('%H:%M:%S')}] --- ALL COMPLETED ---")
sys.stdout.flush()
