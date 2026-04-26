import sqlite3, pickle
from rank_bm25 import BM25Okapi
import re
import os
from neo4j import GraphDatabase

def tokenize_kr(text):
    # 한국어 + 영어 토큰화
    # 2자 이상 토큰만
    tokens = re.findall(r'[가-힣]{2,}|[a-zA-Z]{2,}|\d+', text or '')
    return [t.lower() for t in tokens]

def get_neo4j_ids():
    n_uri = os.environ.get('NEO4J_URI', 'bolt://127.0.0.1:7687')
    n_user = os.environ.get('NEO4J_USERNAME', 'neo4j')
    n_pw = os.environ.get('NEO4J_PASSWORD', 'toss1234')
    
    driver = GraphDatabase.driver(n_uri, auth=(n_user, n_pw))
    try:
        with driver.session() as session:
            res = session.run("MATCH (c:Candidate) RETURN c.id as id")
            return [str(r["id"]) for r in res]
    finally:
        driver.close()

def build():
    db_path = 'candidates.db'
    if not os.path.exists(db_path):
        print(f"Error: {db_path} not found.")
        return

    print("Fetching actual IDs from Neo4j...")
    neo4j_ids = get_neo4j_ids()
    print(f"Found {len(neo4j_ids)} candidates in Neo4j.")

    conn = sqlite3.connect(db_path)
    
    # We use a temporary table to handle large IN clause if needed, 
    # but for ~3000 IDs, a direct parameter list or simple filter is fine.
    # To be safe and efficient, we'll use a placeholder approach.
    
    placeholders = ','.join(['?'] * len(neo4j_ids))
    query = f'''
        SELECT id, name_kr, raw_text, profile_summary, sector
        FROM candidates
        WHERE id IN ({placeholders})
        AND raw_text IS NOT NULL
        AND length(raw_text) > 100
    '''
    
    print(f"Querying SQLite for {len(neo4j_ids)} IDs...")
    rows = conn.execute(query, neo4j_ids).fetchall()

    if not rows:
        print("No valid candidates found for indexing after filtering.")
        conn.close()
        return

    ids = [r[0] for r in rows]
    corpus = []
    for r in rows:
        # name + summary + raw_text 앞 1000자 합쳐서 인덱싱
        combined = f"{r[1] or ''} {r[3] or ''} {r[2][:1000]}"
        corpus.append(tokenize_kr(combined))

    print(f"Tokenizing complete. Starting BM25 indexing for {len(ids)} candidates...")
    bm25 = BM25Okapi(corpus)

    # 저장
    output_path = 'bm25_index.pkl'
    with open(output_path, 'wb') as f:
        pickle.dump({'bm25': bm25, 'ids': ids}, f)

    file_size = os.path.getsize(output_path) / (1024 * 1024)
    print(f'BM25 index built successfully: {len(ids)} candidates saved to {output_path} ({file_size:.2f}MB)')
    conn.close()

if __name__ == "__main__":
    build()
