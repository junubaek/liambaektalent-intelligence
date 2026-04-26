import sqlite3, pickle, os

def check_counts():
    conn = sqlite3.connect('candidates.db')
    cur = conn.cursor()
    
    print("--- SQLite Status ---")
    total = cur.execute('SELECT count(*) FROM candidates').fetchone()[0]
    synced = cur.execute('SELECT count(*) FROM candidates WHERE is_neo4j_synced = 1').fetchone()[0]
    not_synced = cur.execute('SELECT count(*) FROM candidates WHERE is_neo4j_synced = 0').fetchone()[0]
    null_synced = cur.execute('SELECT count(*) FROM candidates WHERE is_neo4j_synced IS NULL').fetchone()[0]
    
    print(f"Total: {total}")
    print(f"is_neo4j_synced = 1: {synced}")
    print(f"is_neo4j_synced = 0: {not_synced}")
    print(f"is_neo4j_synced IS NULL: {null_synced}")
    
    tables = cur.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
    print(f"Tables: {[t[0] for t in tables]}")
    
    print("\n--- BM25 Status ---")
    bm_path = 'bm25_index.pkl'
    if os.path.exists(bm_path):
        with open(bm_path, 'rb') as f:
            data = pickle.load(f)
            print(f"BM25 IDs: {len(data['ids'])}")
            
    print("\n--- Neo4j Status (via Env) ---")
    # I won't run neo4j here to keep it simple, just reporting what I found earlier
    # Neo4j: 3278
    
    conn.close()

if __name__ == "__main__":
    check_counts()
