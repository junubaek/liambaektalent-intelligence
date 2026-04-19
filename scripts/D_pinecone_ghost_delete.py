import json
import sqlite3
import time
from connectors.pinecone_api import PineconeClient

def delete_pinecone_ghosts():
    with open("secrets.json", "r") as f:
        secrets = json.load(f)

    host = secrets.get("PINECONE_HOST", "").rstrip("/")
    if not host.startswith("https://"):
        host = f"https://{host}"
    pc = PineconeClient(api_key=secrets.get("PINECONE_API_KEY"), host=host)
    
    conn = sqlite3.connect("candidates.db")
    c = conn.cursor()
    c.execute("SELECT id FROM candidates WHERE is_duplicate=1 AND is_pinecone_synced=1")
    ghost_ids = [row[0] for row in c.fetchall()]
    
    print(f"Found {len(ghost_ids)} ghost/duplicate candidates in Pinecone.")
    
    success_count = 0
    # Delete one by one to ensure no filter limits hit
    for i, cid in enumerate(ghost_ids):
        # Delete using metadata filter
        # filter parameter in pinecone api 
        # pinecone: delete(filter_meta={"candidate_id": cid}, namespace="resume_vectors")
        # OR delete(filter_meta={"candidate_id": {"$eq": cid}}, namespace="resume_vectors")
        try:
            res = pc.delete(filter_meta={"candidate_id": {"$eq": cid}}, namespace="resume_vectors")
            if res is not None:
                # Update DB
                c.execute("UPDATE candidates SET is_pinecone_synced=0 WHERE id=?", (cid,))
                success_count += 1
                if success_count % 50 == 0:
                    conn.commit()
                    print(f"Deleted {success_count}...")
        except Exception as e:
            print(f"Failed to delete {cid}: {e}")
            
    conn.commit()
    print(f"Successfully deleted vectors for {success_count} ghost candidates!")
    
if __name__ == "__main__":
    delete_pinecone_ghosts()
