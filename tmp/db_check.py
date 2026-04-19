import sqlite3
import json

db_path = "candidates.db"

def check():
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    
    # Query specific names or names with brackets
    query = """
    SELECT c.id, c.name_kr, c.raw_text, p.parsed_json 
    FROM candidates c 
    LEFT JOIN parsing_cache p ON c.id = p.candidate_id 
    WHERE c.name_kr IN ('강민성', '이종구', '김현구', '김대중', '자금', '재무회계', '[자금]', '[재무회계]')
    """
    
    rows = cur.execute(query).fetchall()
    
    for row in rows:
        cid, name, raw_text, parsed_json_str = row
        parsed = json.loads(parsed_json_str) if parsed_json_str else {}
        
        print(f"Name: {name} (ID: {cid})")
        print(f"Profile Summary: {parsed.get('profile_summary', 'MISSING')[:100]}")
        print(f"Careers: {len(parsed.get('careers', []))}")
        print("-" * 40)
        
    print("Done")
    
if __name__ == "__main__":
    check()
