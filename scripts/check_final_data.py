import sqlite3
import json

def check_data():
    conn = sqlite3.connect('candidates.db')
    emails = conn.execute("SELECT count(*) FROM candidates WHERE email IS NOT NULL AND email != ''").fetchone()[0]
    phones = conn.execute("SELECT count(*) FROM candidates WHERE phone IS NOT NULL AND phone != ''").fetchone()[0]
    edus = conn.execute("SELECT count(*) FROM candidates WHERE education_json IS NOT NULL AND education_json != '[]' AND education_json != ''").fetchone()[0]
    
    with open('candidates_cache_jd.json', 'r', encoding='utf-8') as f:
        cache = json.load(f)
        
    namesakes = sum(1 for c in cache if '(' in c.get('name_kr', ''))
    ghosts = sum(1 for c in cache if '무명' in c.get('name_kr', ''))
    
    print(f"--- DATABASE STATE ---")
    print(f"Total Cached Candidates: {len(cache)}")
    print(f"Valid Emails in DB: {emails}")
    print(f"Valid Phones in DB: {phones}")
    print(f"Valid Edus in DB: {edus}")
    
    print(f"\n--- CACHE & CLEANSING STATE ---")
    print(f"Candidates with '무명 / Ghost': {ghosts}")
    print(f"Candidates safely identified as Namesakes (with Job Titles): {namesakes}")

if __name__ == "__main__":
    check_data()
