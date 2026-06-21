import json
import sqlite3
import sys
import os
from openai import OpenAI
from neo4j import GraphDatabase

sys.stdout.reconfigure(encoding='utf-8')
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT_DIR)

from run_neo4j_embedding_expansion import build_emb_text

def main():
    # Load secrets
    with open('secrets.json', 'r', encoding='utf-8') as f:
        secrets = json.load(f)

    oai = OpenAI(api_key=secrets['OPENAI_API_KEY'])
    driver = GraphDatabase.driver(
        secrets['NEO4J_URI'],
        auth=(secrets['NEO4J_USERNAME'], secrets['NEO4J_PASSWORD'])
    )

    conn = sqlite3.connect('candidates.db')
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    target_ids = [
        'f5875fc2-99aa-4605-9742-5ec93f4cd51a', # 김은형
        '07043d62-db55-458e-a43e-2243d30f4065', # 정혜연
        '8454b89a-4474-4787-8c07-3b8a9e937a45'  # 이강원
    ]

    print("=== Fetching Candidate Data from SQLite ===")
    placeholders = ','.join(['?'] * len(target_ids))
    query = f'''
        SELECT id, name_kr, sector, profile_summary, raw_text, current_company, total_years,
               CASE
                 WHEN total_years >= 10 THEN "SENIOR"
                 WHEN total_years >= 5 THEN "MIDDLE"
                 ELSE "JUNIOR"
               END as seniority
        FROM candidates 
        WHERE id IN ({placeholders})
    '''
    cur.execute(query, target_ids)
    rows = cur.fetchall()

    texts = []
    valid_ids = []
    for r in rows:
        text_block = build_emb_text(r)
        print(f"\n--- Embedding Text for {r['name_kr']} ({r['id'][:8]}) ---")
        print(text_block)
        texts.append(text_block)
        valid_ids.append(r['id'])

    if not texts:
        print("No candidates found in database.")
        conn.close()
        driver.close()
        return

    print("\n=== Fetching Embeddings from OpenAI ===")
    resp = oai.embeddings.create(model='text-embedding-3-small', input=texts)

    print("\n=== Updating Neo4j Candidate Embeddings ===")
    with driver.session() as s:
        params = []
        for j, cid in enumerate(valid_ids):
            params.append({'id': cid, 'emb': resp.data[j].embedding})
        
        s.run('''
            UNWIND $batch as item
            MATCH (c:Candidate {id: item.id})
            SET c.embedding = item.emb
        ''', batch=params)
        print("Neo4j database updated successfully.")

    conn.close()
    driver.close()
    print("\nTarget candidate embeddings updated successfully!")

if __name__ == "__main__":
    main()
