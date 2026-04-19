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
    
    conn = sqlite3.connect("candidates.db")
    ghost_ids = [r[0] for r in conn.execute("SELECT id FROM candidates WHERE is_duplicate=1 AND is_pinecone_synced=1").fetchall()]
    
    print(f"Deleting {len(ghost_ids)} from pinecone...")
    
    # We can delete chunks 0-20 to be safe since they are named {cid}_chunk_0
    
    deleted = 0
    for cid in ghost_ids:
        # Instead of metadata filter which might be slow on large indexes, we just delete IDs if we know them:
        vector_ids = [f"{cid}_chunk_{i}" for i in range(15)]
        
        payload = {
            "ids": vector_ids,
            "namespace": "resume_vectors"
        }
        res = requests.post(f"{host}/vectors/delete", json=payload, headers=headers, timeout=10)
        
        if res.status_code == 200:
            conn.execute("UPDATE candidates SET is_pinecone_synced=0 WHERE id=?", (cid,))
            deleted += 1
            if deleted % 50 == 0:
                print(f"Deleted {deleted} candidates.")
                conn.commit()
        else:
            print(f"Error {res.status_code}: {res.text}")
            
    conn.commit()
    print(f"Done! {deleted} candidate vectors removed from pinecone.")
    
if __name__ == "__main__":
    do_pinecone_del()
