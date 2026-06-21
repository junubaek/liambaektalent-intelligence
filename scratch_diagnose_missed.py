import sqlite3
import sys
import os

sys.stdout.reconfigure(encoding='utf-8')
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT_DIR)

from jd_compiler import api_search_v9

db_path = "candidates.db"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

print("=== [1] Candidates Database Status ===")
cursor.execute("""
    SELECT id, name_kr, current_company, sector, is_duplicate 
    FROM candidates 
    WHERE name_kr IN ('정혜연', '이강원', '김은형')
""")
rows = cursor.fetchall()
for r in rows:
    print(f"ID: {r[0]} | Name: {r[1]} | Company: {r[2]} | Sector: {r[3]} | IsDup: {r[4]}")

print("\n=== [2] Run api_search_v9 and Scan Top 30 ===")

queries = [
    ('Kafka 인프라 엔지니어', '정혜연'),
    ('CTO Technical Leader', '이강원'),
    ('CFO Chief Financial Officer', '김은형'),
    ('Technical Program Manager', '안유리')
]

for q, target in queries:
    res = api_search_v9(q)
    matched = res.get('matched', [])
    print(f"\nQuery: '{q}' | Target Name: '{target}' | Total Matches: {len(matched)}")
    
    found_rank = -1
    for rank, cand in enumerate(matched[:30]):
        cname = cand.get('name_kr', '')
        cid = cand.get('id', '')
        ccompany = cand.get('current_company', '')
        csector = cand.get('sector', '')
        
        # Output Top 10 first
        if rank < 10:
            print(f"  {rank+1}. {cname} ({ccompany} | {csector}) - {cid[:8]}")
            
        if cname == target:
            found_rank = rank + 1
            if rank >= 10:
                print(f"  ... Found {cname} at Rank {found_rank}: ({ccompany} | {csector})")
                
    if found_rank == -1:
        # Check beyond Top 30
        for rank, cand in enumerate(matched[30:]):
            if cand.get('name_kr', '') == target:
                found_rank = rank + 31
                print(f"  -> Found target beyond Top 30: Rank {found_rank}")
                break
                
    if found_rank == -1:
        print(f"  -> TARGET NOT FOUND in all search results.")

print("\n=== [3] Candidates Profile Summaries ===")
cursor.execute("""
    SELECT name_kr, profile_summary 
    FROM candidates 
    WHERE name_kr IN ('정혜연', '이강원', '김은형')
    AND is_duplicate = 0
""")
rows = cursor.fetchall()
for r in rows:
    print(f"\n--- {r[0]} profile_summary ---")
    print(r[1])

conn.close()
