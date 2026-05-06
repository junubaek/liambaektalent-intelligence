import sqlite3
import json
import os
import re
import time
from connectors.gemini_api import GeminiClient
from resume_parser import ResumeParser

def unified_cleanup_and_reparse(batch_limit=50):
    conn = sqlite3.connect('candidates.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # --- PHASE 1: Metadata Cleanup ---
    print("\n--- Phase 1: Metadata Cleanup ---")
    
    # 1. Recover Garbled Names
    print("Recovering garbled names from raw_text...")
    cursor.execute("SELECT id, name_kr, raw_text FROM candidates WHERE name_kr LIKE '%%' OR name_kr IS NULL OR name_kr = ''")
    rows = cursor.fetchall()
    recovered_count = 0
    for row in rows:
        text = row['raw_text'] if row['raw_text'] else ""
        # Heuristic: Find '성명 : XXX' or '이 름 : XXX'
        match = re.search(r'(?:성명|이\s*름)\s*[:：]\s*([가-힣]{2,4})', text)
        if match:
            new_name = match.group(1)
            cursor.execute("UPDATE candidates SET name_kr = ? WHERE id = ?", (new_name, row['id']))
            recovered_count += 1
    print(f"Recovered {recovered_count} names.")
    
    # 2. Merge Duplicates by Email
    print("Merging duplicates by email...")
    cursor.execute("""
        SELECT email, COUNT(*) as count 
        FROM candidates 
        WHERE email IS NOT NULL AND email != '' AND is_duplicate = 0
        GROUP BY email 
        HAVING count > 1
    """)
    dup_emails = cursor.fetchall()
    merged_count = 0
    for d in dup_emails:
        # Get all records for this email
        cursor.execute("SELECT id, name_kr, is_parsed, length(raw_text) as text_len FROM candidates WHERE email = ? AND is_duplicate = 0 ORDER BY is_parsed DESC, text_len DESC", (d['email'],))
        records = cursor.fetchall()
        master_id = records[0]['id']
        for r in records[1:]:
            cursor.execute("UPDATE candidates SET is_duplicate = 1, duplicate_of = ? WHERE id = ?", (master_id, r['id']))
            merged_count += 1
    print(f"Merged {merged_count} duplicate records.")
    
    conn.commit()
    
    # --- PHASE 2: Targeted Re-parsing ---
    print("\n--- Phase 2: Targeted Re-parsing ---")
    
    # Initialize Gemini
    if not os.path.exists('secrets.json'):
        print("secrets.json not found. Skipping Phase 2.")
        return
    
    with open('secrets.json', 'r', encoding='utf-8') as f:
        secrets = json.load(f)
    
    client = GeminiClient(secrets['GEMINI_API_KEY'])
    parser = ResumeParser(client)
    
    # Identify records needing re-parsing
    # Criteria: Never parsed OR (Missing career/education and is_parsed=1)
    query = """
    SELECT id, name_kr, raw_text, careers_json, education_json 
    FROM candidates 
    WHERE is_duplicate = 0 AND (
        is_parsed = 0 
        OR (is_parsed = 1 AND (careers_json IS NULL OR careers_json = '[]' OR careers_json = ''))
        OR (is_parsed = 1 AND (education_json IS NULL OR education_json = '[]' OR education_json = ''))
    )
    LIMIT ?
    """
    cursor.execute(query, (batch_limit,))
    to_parse = cursor.fetchall()
    
    print(f"Found {len(to_parse)} records to re-parse (Batch Limit: {batch_limit}).")
    
    success_count = 0
    for row in to_parse:
        cid = row['id']
        name = row['name_kr']
        text = row['raw_text']
        
        print(f"  Parsing [{name}] ({cid})...", end='', flush=True)
        try:
            # Widen parsing: Increase context or ensure deep extraction
            # Here we just use the existing parser but we could modify the prompt if needed
            result = parser.parse(text)
            
            if result:
                # Map result to DB columns
                # Note: The schema from Gemini parser needs to be mapped to candidates.db columns
                profile = result.get('candidate_profile', {})
                patterns = result.get('patterns', [])
                
                # Convert list to JSON string for DB
                # Note: In this project, careers_json often stores the summary or structured objects
                careers_json = json.dumps(patterns, ensure_ascii=False)
                # Education might be extracted from context_tags or experience_summary in v8.0 prompt
                # Let's check if we can get more.
                
                # Update DB
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
                success_count += 1
                print(" OK")
            else:
                print(" FAILED (Empty Result)")
        except Exception as e:
            print(f" ERROR: {e}")
            
        # Rate limiting sleep
        time.sleep(1)
        
    conn.commit()
    print(f"\nPhase 2 Complete. Successfully parsed {success_count} records.")
    conn.close()

if __name__ == "__main__":
    # Start with a safe batch of 50 to avoid hitting limits too hard
    unified_cleanup_and_reparse(batch_limit=50)
