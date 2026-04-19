import sys
import os
import json
import sqlite3

sys.stdout.reconfigure(encoding='utf-8')
ROOT_DIR = r"c:\Users\cazam\Downloads\이력서자동분석검색시스템"
sys.path.append(ROOT_DIR)

print("━━━━━━━━━━━━━━━━━━━━\n1. Pinecone 샘플 3개 확인\n━━━━━━━━━━━━━━━━━━━━")
try:
    from connectors.pinecone_api import PineconeClient
    with open(os.path.join(ROOT_DIR, "secrets.json"), "r", encoding="utf-8") as f:
        secrets = json.load(f)
    
    # Needs a host/index config
    index_host = secrets.get("PINECONE_HOST", "").rstrip("/")
    if not index_host.startswith("https://"):
        index_host = f"https://{index_host}"
        
    pc = PineconeClient(secrets.get("PINECONE_API_KEY", ""), index_host)
    
    # Query with a dummy vector to get records
    dummy_vec = [0.01] * 1536
    res = pc.query(dummy_vec, top_k=3, namespace="candidates_v4")
    
    if res and "matches" in res:
        for idx, match in enumerate(res["matches"]):
            print(f"-- Sample {idx+1} --")
            print(f"ID: {match.get('id')}")
            meta = match.get("metadata", {})
            print(f"Metadata Keys: {list(meta.keys())}")
            print(f"Text Preview (first 100 chars): {meta.get('text', '')[:100]}...")
            print()
    else:
        # Fallback to candidates_v4_2 or something?
        res2 = pc.query(dummy_vec, top_k=3, namespace="history_v4_2")
        if res2 and "matches" in res2:
            print("Found in history_v4_2 instead")
            for idx, match in enumerate(res2["matches"]):
                print(f"-- Sample {idx+1} --")
                print(f"ID: {match.get('id')}")
                meta = match.get("metadata", {})
                print(f"Text Preview (first 100 chars): {meta.get('text', '')[:100]}...")
                print()
        else:
            print("No matches found in candidates_v4 or history_v4_2.")
except Exception as e:
    import traceback
    traceback.print_exc()

print("━━━━━━━━━━━━━━━━━━━━\n3. 예상 벡터 수 (청크) 계산\n━━━━━━━━━━━━━━━━━━━━")
try:
    db_path = os.path.join(ROOT_DIR, "candidates.db")
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("SELECT raw_text FROM candidates WHERE is_duplicate=0 AND is_parsed=1 AND raw_text IS NOT NULL")
    rows = cur.fetchall()
    
    total_candidates = len(rows)
    total_chunks = 0
    chunk_size = 800 # Assume v9 architecture standard
    overlap = 100
    
    for row in rows:
        text = row[0]
        if len(text) < 100: continue
        # Calculate chunks based on sliding window simply:
        chunks = max(1, (len(text) - overlap) // (chunk_size - overlap))
        # Or more accurately, how many chunks of size 800
        total_chunks += chunks
        
    avg = total_chunks / total_candidates if total_candidates > 0 else 0
    est_total = avg * 2468 # currently synchronized base
    print(f"총 유효 후보자: {total_candidates}명")
    print(f"평균 청크 수 (단순 길이 {chunk_size}자 기준): {avg:.2f} 개/명")
    print(f"예상 벡터 수 (2,468명 기준): {int(est_total)} 개 (현재 5,665개)")
except Exception as e:
    print(f"DB Error: {e}")
