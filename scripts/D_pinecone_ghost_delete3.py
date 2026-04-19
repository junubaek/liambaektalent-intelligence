import json
import requests
import sqlite3

def do_pinecone_del():
    with open("secrets.json", "r") as f:
        secrets = json.load(f)

    host = secrets.get("PINECONE_HOST", "").rstrip("/")
    if not host.startswith("https://"):
        host = f"https://{host}"
        
    headers = {
        "Api-Key": secrets.get("PINECONE_API_KEY"),
        "Content-Type": "application/json"
    }
    
    conn = sqlite3.connect("candidates.db", timeout=15)
    c = conn.cursor()
    ghost_ids = [r[0] for r in c.execute("SELECT id FROM candidates WHERE is_duplicate=1 AND is_pinecone_synced=1").fetchall()]
    print(f"Loaded {len(ghost_ids)} ghost ids to delete.")
    
    # We delete in batches of 200 vector IDs per request (Pinecone limit is usually 1000)
    # Each candidate could have 10-20 chunks. So we batch say 10 candidates at a time.
    
    deleted_cands = 0
    batch_size = 10
    
    for i in range(0, len(ghost_ids), batch_size):
        batch = ghost_ids[i:i+batch_size]
        
        vector_ids = []
        for cid in batch:
            vector_ids.extend([f"{cid}_chunk_{j}" for j in range(15)])
            vector_ids.append(str(cid)) # Just in case it's 1:1 ID
            
        payload = {
            "ids": vector_ids,
            "namespace": "resume_vectors"
        }
        
        try:
            res = requests.post(f"{host}/vectors/delete", json=payload, headers=headers, timeout=10)
            if res.status_code == 200:
                for cid in batch:
                    c.execute("UPDATE candidates SET is_pinecone_synced=0 WHERE id=?", (cid,))
                conn.commit()
                deleted_cands += len(batch)
                print(f"Deleted {deleted_cands}/{len(ghost_ids)}")
            else:
                print(f"Error {res.status_code}: {res.text}")
        except Exception as e:
            print(f"Failed HTTP req: {e}")
            
    conn.commit()
    print("Done!")

if __name__ == "__main__":
    do_pinecone_del()
