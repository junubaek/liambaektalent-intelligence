import json
import urllib.request
import urllib.error
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
    
    deleted_cands = 0
    batch_size = 10
    
    namespaces = ["resume_vectors", "ns1", "v6.2-vs"]
    
    for i in range(0, len(ghost_ids), batch_size):
        batch = ghost_ids[i:i+batch_size]
        
        vector_ids = []
        for cid in batch:
            vector_ids.extend([f"{cid}_chunk_{j}" for j in range(15)])
            vector_ids.append(str(cid))
            
        success = False
        for ns in namespaces:
            payload = {"ids": vector_ids, "namespace": ns}
            data = json.dumps(payload).encode('utf-8')
            req = urllib.request.Request(f"{host}/vectors/delete", data=data, headers=headers)
            
            try:
                with urllib.request.urlopen(req, timeout=10) as res:
                    succ = json.loads(res.read().decode('utf-8'))
                    success = True
            except Exception as e:
                pass
                
        if success:
            for cid in batch:
                c.execute("UPDATE candidates SET is_pinecone_synced=0 WHERE id=?", (cid,))
            conn.commit()
            deleted_cands += len(batch)
            print(f"Deleted {deleted_cands}/{len(ghost_ids)}")
            
    conn.commit()
    print("Done!")

if __name__ == "__main__":
    do_pinecone_del()
