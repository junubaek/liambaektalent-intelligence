import os, sqlite3, json, sys, uuid
sys.stdout.reconfigure(encoding='utf-8')

# Root directory check
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT_DIR)

from neo4j import GraphDatabase
from openai import OpenAI
from connectors.pinecone_api import PineconeClient
from batch_pinecone_sync import chunk_text

with open('secrets.json', 'r', encoding='utf-8') as f:
    secrets = json.load(f)

# Clients
openai_client = OpenAI(api_key=secrets["OPENAI_API_KEY"])
n_uri = secrets.get("NEO4J_URI", "neo4j://127.0.0.1:7687")
n_user = secrets.get("NEO4J_USERNAME", "neo4j")
n_pw = secrets.get("NEO4J_PASSWORD", "toss1234")
driver = GraphDatabase.driver(n_uri, auth=(n_user, n_pw))

pc_host = secrets.get("PINECONE_HOST", "").rstrip("/")
if not pc_host.startswith("https://"): pc_host = f"https://{pc_host}"
pinecone_client = PineconeClient(secrets.get("PINECONE_API_KEY", ""), pc_host)

def sync_to_neo4j(row):
    with driver.session() as session:
        session.run("""
            MERGE (c:Candidate {id: $id})
            SET c.name = $name_kr, c.phone = $phone, c.email = $email,
                c.current_company = $current_company, c.profile_summary = $summary,
                c.total_years = $total_years, c.sector = $sector
        """, id=row['id'], name_kr=row['name_kr'], phone=row['phone'], email=row['email'], 
             current_company=row['current_company'], summary=row['profile_summary'], 
             total_years=row['total_years'], sector=row['sector'])
        
        # Skill edges if careers_json or raw_text exists? 
        # For simplicity, we just sync the node properties. 
        # If we want skills, we'd need to re-parse with Gemini, but the user didn't ask for that.
        # However, let's at least sync the node so it's searchable.
    return True

def sync_to_pinecone(row):
    text = row['raw_text']
    if not text: return False
    chunks = chunk_text(text)
    if not chunks: return True
    
    response = openai_client.embeddings.create(model="text-embedding-3-small", input=chunks)
    vectors = []
    for i, emb in enumerate(response.data):
        vectors.append({
            "id": f"{row['id']}_chunk_{i}",
            "values": emb.embedding,
            "metadata": {"candidate_id": row['id'], "chunk_index": i}
        })
    pinecone_client.upsert(vectors, namespace="resume_vectors")
    return True

def main():
    conn = sqlite3.connect('candidates.db')
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    
    cur.execute('''
        SELECT * FROM candidates 
        WHERE is_duplicate = 0 AND (is_neo4j_synced = 0 OR is_pinecone_synced = 0)
    ''')
    rows = cur.fetchall()
    print(f"Found {len(rows)} candidates to sync.")
    
    for row in rows:
        print(f"Syncing {row['name_kr']} ({row['id'][:8]})...")
        neo_ok = sync_to_neo4j(row)
        pinecone_ok = sync_to_pinecone(row)
        
        if neo_ok and pinecone_ok:
            cur.execute('UPDATE candidates SET is_neo4j_synced = 1, is_pinecone_synced = 1 WHERE id = ?', (row['id'],))
            conn.commit()
            print("  Done.")
        else:
            print("  Failed.")
            
    conn.close()
    driver.close()

if __name__ == "__main__":
    main()
