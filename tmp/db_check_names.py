import sqlite3
import json

db_path = "candidates.db"

def check():
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    
    names_to_check = ['강민성', '이종구', '김현구', '김대중']
    query = f"SELECT c.id, c.name_kr, c.raw_text, p.parsed_json FROM candidates c LEFT JOIN parsing_cache p ON c.id = p.candidate_id WHERE c.name_kr IN ({','.join(['?']*len(names_to_check))})"
    
    rows = cur.execute(query, names_to_check).fetchall()
    
    for row in rows:
        cid, name, raw_text, parsed_json_str = row
        parsed = json.loads(parsed_json_str) if parsed_json_str else {}
        
        print(f"Name: {name} (ID: {cid})")
        print(f"Raw Text: {raw_text[:200] if raw_text else 'MISSING'}")
        print(f"Profile Summary: {parsed.get('profile_summary', 'MISSING')[:100]}")
        print(f"Careers Count: {len(parsed.get('careers', []))}")
        print("-" * 40)
        
    print("Done")
    
if __name__ == "__main__":
    check()
