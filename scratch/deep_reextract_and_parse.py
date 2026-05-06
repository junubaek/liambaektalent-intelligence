import sqlite3
import json
import os
from connectors.gdrive_api import GDriveConnector
from connectors.gemini_api import GeminiClient
from resume_parser import ResumeParser

def deep_reextract_and_parse():
    # 1. Load targets
    with open('reparse_targets.json', 'r', encoding='utf-8') as f:
        targets = json.load(f)
        
    if not os.path.exists('secrets.json'):
        print("secrets.json not found.")
        return
        
    with open('secrets.json', 'r', encoding='utf-8') as f:
        secrets = json.load(f)
        
    # 2. Initialize Clients
    gdrive = GDriveConnector()
    gemini = GeminiClient(secrets['GEMINI_API_KEY'])
    parser = ResumeParser(gemini)
    
    conn = sqlite3.connect('candidates.db')
    cursor = conn.cursor()
    
    print(f"--- Deep Processing {len(targets)} Targets ---")
    
    for t in targets:
        cid = t['id']
        name = t['name_kr']
        url = t['google_drive_url']
        
        print(f"Processing [{name}] ({cid})...")
        
        # Step A: Re-extract text from GDrive
        try:
            print(f"  Extracting text from: {url}")
            full_text = gdrive.extract_text_from_url(url)
            
            if not full_text or len(full_text) < 100:
                print(f"  [WARN] Extracted text too short ({len(full_text) if full_text else 0} chars).")
                # If extraction fails, we can't do much more for now.
                continue
            
            print(f"  Extraction success ({len(full_text)} chars). Updating raw_text...")
            cursor.execute("UPDATE candidates SET raw_text = ? WHERE id = ?", (full_text, cid))
            
            # Step B: Parse with AI
            print(f"  Parsing with Gemini AI...")
            result = parser.parse(full_text)
            
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
                print("  [SUCCESS] Data updated.")
            else:
                print("  [FAILED] AI parsing returned empty result.")
                
        except Exception as e:
            print(f"  [ERROR] {e}")
            
        conn.commit()
        
    conn.close()
    print("--- Deep Processing Complete ---")

if __name__ == "__main__":
    deep_reextract_and_parse()
