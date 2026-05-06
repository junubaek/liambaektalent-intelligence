import sqlite3
import json
import os
import re
from connectors.gemini_api import GeminiClient
from resume_parser import ResumeParser

def execute_final_cleanup():
    conn = sqlite3.connect('candidates.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # 1. DELETE the 33 invalid records
    with open('candidates_to_delete.json', 'r', encoding='utf-8') as f:
        to_delete = json.load(f)
    
    print(f"--- Deleting {len(to_delete)} invalid records ---")
    deleted_count = 0
    for r in to_delete:
        cursor.execute("DELETE FROM candidates WHERE id = ?", (r['id'],))
        deleted_count += 1
    print(f"Successfully deleted {deleted_count} records.")
    
    # 2. RECOVER and RE-PARSE the remaining 17 records
    # We identify them as: is_duplicate=0 AND (careers_json IS NULL OR '[]' OR '')
    # (Excluding the ones we just deleted)
    query = """
    SELECT id, name_kr, email, raw_text 
    FROM candidates 
    WHERE is_duplicate = 0 
      AND (careers_json IS NULL OR careers_json = '[]' OR careers_json = '')
    """
    rows = cursor.execute(query).fetchall()
    print(f"\n--- Recovering and Re-parsing {len(rows)} potentially valid records ---")
    
    # Initialize Gemini
    if not os.path.exists('secrets.json'):
        print("secrets.json not found. Committing deletions only.")
        conn.commit()
        conn.close()
        return
    
    with open('secrets.json', 'r', encoding='utf-8') as f:
        secrets = json.load(f)
    
    client = GeminiClient(secrets['GEMINI_API_KEY'])
    parser = ResumeParser(client)
    
    recovered_names = 0
    reparsed_count = 0
    
    for row in rows:
        cid = row['id']
        text = row['raw_text'] if row['raw_text'] else ""
        
        # Step A: Recover name if garbled
        match = re.search(r'(?:성명|이\s*름)\s*[:：]\s*([가-힣]{2,4})', text)
        if match:
            new_name = match.group(1)
            cursor.execute("UPDATE candidates SET name_kr = ? WHERE id = ?", (new_name, cid))
            recovered_names += 1
            print(f"  Recovered name: {new_name}")
        
        # Step B: Re-parse
        print(f"  Re-parsing [{cid}]...", end='', flush=True)
        try:
            result = parser.parse(text)
            if result:
                profile = result.get('candidate_profile', {})
                patterns = result.get('patterns', [])
                careers_json = json.dumps(patterns, ensure_ascii=False)
                
                cursor.execute("""
                    UPDATE candidates 
                    SET is_parsed = 1,
                        careers_json = ?,
                        total_years = ?,
                        sector = ?,
                        profile_summary = ?,
                        updated_at = datetime('now')
                    WHERE id = ?
                """, (
                    careers_json,
                    profile.get('total_years_experience', 0),
                    ", ".join(profile.get('main_sectors', [])),
                    "\n".join(profile.get('experience_summary', [])) if isinstance(profile.get('experience_summary'), list) else profile.get('experience_summary', ''),
                    cid
                ))
                reparsed_count += 1
                print(" OK")
            else:
                print(" FAILED")
        except Exception as e:
            print(f" ERROR: {e}")
            
    conn.commit()
    print(f"\nCleanup Complete.")
    print(f"Total Deleted: {deleted_count}")
    print(f"Names Recovered: {recovered_names}")
    print(f"Records Reparsed: {reparsed_count}")
    
    conn.close()

if __name__ == "__main__":
    execute_final_cleanup()
