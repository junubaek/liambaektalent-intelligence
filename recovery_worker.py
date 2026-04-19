import sqlite3
import datetime
import time
import json
import hashlib
from app.database import SessionLocal # in case we need it, but using raw sqlite3 mostly
from collections import namedtuple

# Reuse specific worker functions
from dynamic_parser_v2 import parse_resume_batch, save_edges
from batch_pinecone_sync import pinecone_client, openai_client, chunk_text

DB_PATH = 'candidates.db'
REPORT_PATH = 'audit_report.txt'

def append_to_audit_report(parse_count, neo4j_count, pinecone_count):
    now_str = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')
    log_line = f"[{now_str}] Recovery: 파싱 {parse_count}건, Neo4j {neo4j_count}건, Pinecone {pinecone_count}건 복구"
    with open(REPORT_PATH, 'a', encoding='utf-8') as f:
        f.write("\n" + log_line + "\n")
    print(log_line)

def run_pinecone_sync(candidate_id, name_kr, raw_text):
    chunks = chunk_text(raw_text)
    if not chunks: return True
    try:
        response = openai_client.embeddings.create(
            model="text-embedding-3-small",
            input=chunks
        )
        vectors_to_upsert = []
        for i, emb_data in enumerate(response.data):
            vectors_to_upsert.append({
                "id": f"{candidate_id}_chunk_{i}",
                "values": emb_data.embedding,
                "metadata": {
                    "candidate_id": candidate_id,
                    "chunk_index": i
                }
            })
        return pinecone_client.upsert(vectors_to_upsert, namespace="resume_vectors")
    except Exception as e:
        print(f"❌ Pinecone API Error for {name_kr}: {e}")
        return False

def recovery_worker():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # Find candidates failed more than 2 hours ago
    two_hours_ago = (datetime.datetime.now() - datetime.timedelta(hours=2)).strftime('%Y-%m-%d %H:%M:%S')
    
    query = """
    SELECT id, document_hash, name_kr, is_parsed, is_neo4j_synced, is_pinecone_synced, raw_text, last_error
    FROM candidates 
    WHERE (is_parsed = 0 OR is_neo4j_synced = 0 OR is_pinecone_synced = 0)
      AND updated_at < ?
    """
    targets = cur.execute(query, (two_hours_ago,)).fetchall()
    
    if not targets:
        print("No candidates need recovery.")
        return
        
    print(f"Found {len(targets)} candidates to recover.")

    recovered_parsed = 0
    recovered_neo4j = 0
    recovered_pinecone = 0

    for row in targets:
        cid, doc_hash, name_kr, is_parsed, is_neo4j, is_pc, raw_text, last_error = row
        print(f"\nAttempting recovery for [{name_kr}] (ID: {cid})")
        
        # Determine operations
        needs_parse = (not is_parsed) or (not is_neo4j)  # Needs fresh graph generation if either is missing
        needs_pinecone = not is_pc
        
        success_all = True
        
        # 1. Gemini + Neo4j parse & save
        if needs_parse:
            print(" -> Needs Gemini Parse / Neo4j Sync")
            # We must derive a pseudo candidate_name for saving. The file base name is usually not directly tracked in SQLite, 
            # but mapping 'name_kr' to it is mostly acceptable for dynamic_parser_v2's base logic if missing.
            # Usually candidate_name = name_kr when purely from DB fallback.
            candidate_base = name_kr  
            if raw_text:
                for attempt in range(1, 4):  # 1 to 3
                    try:
                        batch_dict = {candidate_base: raw_text}
                        parsed_res = parse_resume_batch(batch_dict)
                        if candidate_base in parsed_res:
                            edges = parsed_res[candidate_base]
                            save_edges(candidate_base, edges, raw_text)
                            # Flag update
                            cur.execute("UPDATE candidates SET is_parsed = 1, is_neo4j_synced = 1, last_error = NULL WHERE id = ?", (cid,))
                            conn.commit()
                            recovered_parsed += (not is_parsed)
                            recovered_neo4j += (not is_neo4j)
                            print(f" -> Success Parse / Neo4j")
                            break
                        else:
                            raise Exception("Gemini returned empty results")
                    except Exception as e:
                        print(f" -> Parse Attempt {attempt} failed: {e}")
                        if attempt < 3:
                            sleep_time = 60 * (2 ** (attempt - 1)) # Backoff: 60s, 120s
                            print(f"    Waiting {sleep_time} seconds before retry...")
                            time.sleep(sleep_time)
                        else:
                            cur.execute("UPDATE candidates SET last_error = ? WHERE id = ?", (str(e), cid))
                            conn.commit()
                            success_all = False
            else:
                success_all = False
                
        # 2. Pinecone 
        if needs_pinecone and success_all:
            print(" -> Needs Pinecone Sync")
            for attempt in range(1, 4):
                try:
                    if run_pinecone_sync(cid, name_kr, raw_text):
                        cur.execute("UPDATE candidates SET is_pinecone_synced = 1, last_error = NULL WHERE id = ?", (cid,))
                        conn.commit()
                        recovered_pinecone += 1
                        print(" -> Success Pinecone")
                        break
                    else:
                        raise Exception("Pinecone client returned False")
                except Exception as e:
                    print(f" -> Pinecone Attempt {attempt} failed: {e}")
                    if attempt < 3:
                        sleep_time = 60 * (2 ** (attempt - 1))
                        print(f"    Waiting {sleep_time} seconds before retry...")
                        time.sleep(sleep_time)
                    else:
                        cur.execute("UPDATE candidates SET last_error = ? WHERE id = ?", (str(e), cid))
                        conn.commit()
                        success_all = False
                        
    conn.close()
    if recovered_parsed > 0 or recovered_neo4j > 0 or recovered_pinecone > 0:
        append_to_audit_report(recovered_parsed, recovered_neo4j, recovered_pinecone)

if __name__ == "__main__":
    recovery_worker()
