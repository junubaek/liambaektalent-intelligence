import sqlite3
import json
import time
from datetime import datetime
from openai import OpenAI
from neo4j import GraphDatabase
from connectors.pinecone_api import PineconeClient

def main():
    print("Starting Step 4: Phase 3 Neo4j & Pinecone Resync...")
    with open("secrets.json", "r") as f:
        secrets = json.load(f)
        
    openai_client = OpenAI(api_key=secrets.get("OPENAI_API_KEY", ""))
    pc_host = secrets.get("PINECONE_HOST", "").rstrip("/")
    if not pc_host.startswith("https://"):
        pc_host = f"https://{pc_host}"
    pc = PineconeClient(secrets.get("PINECONE_API_KEY", ""), pc_host)
    
    driver = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "toss1234"))
    conn = sqlite3.connect("candidates.db", timeout=20)
    c = conn.cursor()
    
    with open('candidates_cache_jd.json', 'r', encoding='utf-8') as f:
        cache = {str(item['id']).replace('-', ''): item for item in json.load(f)}

    # We need to resync those properly parsed but maybe not vector-synced
    # is_parsed=1 and (is_neo4j_synced=0 OR is_pinecone_synced=0) ?
    # Let's just blindly re-sync all candidates whose updated_at is very recent?
    # Actually, we can just sync the ones where we set is_pinecone_synced=0 or just updated ones.
    # The prompt says: "재파싱된 후보자 대상으로만" => They have been parsed recently TODAY.
    today_str = datetime.now().strftime("%Y-%m-%d")
    c.execute("SELECT id, document_hash, name_kr FROM candidates WHERE is_duplicate=0 AND is_parsed=1 AND updated_at LIKE ?", (f"{today_str}%",))
    targets = c.fetchall()
    
    total = len(targets)
    print(f"Found {total} recently reparsed candidates to resync.")
    
    success = 0
    fail = 0
    
    session = driver.session()
    
    for i, row in enumerate(targets):
        cid, doc_hash, name = row
        cid_str = str(cid).replace('-', '')
        cinfo = cache.get(cid_str, {})
        
        summary = cinfo.get("summary", "")
        current_company = cinfo.get("current_company", "")
        sector = cinfo.get("sector", "미분류")
        raw_text = cinfo.get("raw_text", "")
        
        if not summary:
            continue
            
        try:
            # 1. Update Neo4j Properties
            session.run("""
                MATCH (n:Candidate {id: $cid})
                SET n.summary = $summary,
                    n.current_company = $company,
                    n.sector = $sector
            """, cid=str(cid), summary=summary, company=current_company, sector=sector)
            
            # 2. Pinecone Delete (if any exists)
            try:
                pc.delete(filter_meta={"candidate_id": str(cid)}, namespace="resume_vectors")
            except Exception as e:
                pass # Might not exist, ignore
                
            # 3. Pinecone Re-embed Upsert
            # Use chunks of 500 chars (approx 1500 chars per 3 chunks as standard)
            chunks = [raw_text[j:j+1000] for j in range(0, len(raw_text), 800)] if raw_text else [summary]
            if chunks:
                emb_res = openai_client.embeddings.create(model="text-embedding-3-small", input=chunks)
                vectors = []
                for idx, ed in enumerate(emb_res.data):
                    vectors.append({
                        "id": f"{cid}_chunk_{idx}",
                        "values": ed.embedding,
                        "metadata": {
                            "candidate_id": str(cid),
                            "chunk_index": idx
                        }
                    })
                pc.upsert(vectors, namespace="resume_vectors")
                
            # Mark synced
            c.execute("UPDATE candidates SET is_pinecone_synced=1, is_neo4j_synced=1 WHERE id=?", (cid,))
            success += 1
            
        except Exception as e:
            fail += 1
            print(f"Failed resync for {name}: {e}")
            
        if (i+1) % 50 == 0:
            print(f"Progress: {i+1}/{total} (Success: {success}, Fail: {fail})")
            conn.commit()
            
    conn.commit()
    session.close()
    driver.close()
    conn.close()
    print("Resync Completed!")

if __name__ == "__main__":
    main()
