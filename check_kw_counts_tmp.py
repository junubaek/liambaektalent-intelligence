import sqlite3
from run_neo4j_embedding_expansion import CANONICAL_LOWER

def check_samples():
    conn = sqlite3.connect('candidates.db')
    cur = conn.cursor()
    cur.execute('SELECT name_kr, raw_text FROM candidates LIMIT 20')
    rows = cur.fetchall()
    
    print(f"{'Name':<15} | {'Keyword Count':<15}")
    print("-" * 35)
    
    for name, raw in rows:
        raw_lower = (raw or '').lower()
        kw_set = set()
        for src, tgt in CANONICAL_LOWER.items():
            if src in raw_lower:
                kw_set.add(tgt)
        print(f"{name:<15} | {len(kw_set):<15}")
    
    conn.close()

if __name__ == "__main__":
    check_samples()
