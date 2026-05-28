import sqlite3
import json

conn = sqlite3.connect('candidates.db')
cur = conn.cursor()

# Get one parsing_cache record
cur.execute("SELECT candidate_id, parsed_json FROM parsing_cache LIMIT 1")
row = cur.fetchone()
if row:
    print("Candidate ID:", row[0])
    pdict = json.loads(row[1])
    print("Keys in parsed_json:", pdict.keys())
    
    # Check careers
    careers = pdict.get('careers', [])
    print(f"Careers count: {len(careers)}")
    if careers:
        print("First career keys:", careers[0].keys())
        if 'skills_used' in careers[0]:
            print("First career skills_used:", careers[0]['skills_used'])
        if 'skills' in careers[0]:
            print("First career skills:", careers[0]['skills'])
            
conn.close()
