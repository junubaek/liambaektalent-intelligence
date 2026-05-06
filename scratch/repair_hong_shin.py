
import sqlite3
import json
import sys
import os
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(ROOT_DIR)
from connectors.gemini_api import GeminiClient
from resume_parser import ResumeParser

def repair_candidates(target_ids):
    secrets = json.load(open('secrets.json'))
    gemini = GeminiClient(api_key=secrets['GEMINI_API_KEY'])
    parser = ResumeParser(gemini)
    
    conn = sqlite3.connect('candidates.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    for cid in target_ids:
        print(f"Repairing candidate: {cid}")
        cursor.execute("SELECT name_kr, raw_text FROM candidates WHERE id = ?", (cid,))
        row = cursor.fetchone()
        if not row:
            print(f"Candidate {cid} not found.")
            continue
            
        name = row['name_kr']
        raw_text = row['raw_text']
        
        # Deep Re-parsing
        parsed = parser.parse(raw_text)
        if not parsed:
            print(f"Parsing failed for {name}")
            continue
            
        # Update metadata
        # sector, profile_summary, birth_year, total_years, education_json, careers_json
        
        # Mapping Sector (v8.0 schema)
        profile = parsed.get('candidate_profile', {})
        basics = parsed.get('basics', {})
        
        main_sectors = profile.get('main_sectors', [])
        sector_str = ", ".join(main_sectors) if main_sectors else basics.get('canonical_role', '미분류')
        
        # careers_json and education_json might be in 'basics' or root depending on version
        # Let's check common keys
        careers = parsed.get('careers') or basics.get('careers') or []
        education = parsed.get('education') or basics.get('education') or []
        
        # Ensure total_years is a float
        total_years = profile.get('total_years_experience', 0.0)
        if isinstance(total_years, list) and total_years:
            total_years = total_years[0]
        try:
            total_years = float(total_years)
        except:
            total_years = 0.0
            
        # Ensure experience_summary is a string
        exp_summary = profile.get('experience_summary', '')
        if isinstance(exp_summary, list):
            exp_summary = "\n".join(exp_summary)
            
        cursor.execute("""
            UPDATE candidates 
            SET sector = ?, 
                profile_summary = ?, 
                total_years = ?, 
                careers_json = ?, 
                education_json = ?,
                is_parsed = 1,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (
            sector_str,
            exp_summary,
            total_years,
            json.dumps(careers, ensure_ascii=False),
            json.dumps(education, ensure_ascii=False),
            cid
        ))
        print(f"Update complete for {name} ({sector_str}, {total_years} years)")
        
    conn.commit()
    conn.close()

if __name__ == "__main__":
    # Master IDs
    # 김승현: 1d8f0081-06e8-4851-b239-a18b82f4e2db
    # 성장현: 76773431-0ace-4a68-96fc-2954daa6eb72
    # 이민지: 6004cf18-e163-4735-a364-b8ce9ce19319
    # 홍주영: 6581caaa-83df-4fc9-875e-8358d0ad876d
    # 신권철: 8ffb31e4-20ce-4904-bb76-e3bad468fe7f
    repair_candidates([
        '8c510537-4385-471b-adb7-694f7154467e',
        'e262bbeb-df44-4a11-a702-e2a71c8be0a7',
        '9f1c353e-a74e-4c89-8249-606e97ddcc9b',
        '003aac23-613c-4c4b-93b6-6ed1038c78f9',
        '32e22567-1b6f-81e1-b8fc-c946f1c6f5c4',
        'f0728481-bfd4-4d10-9aa3-afe3ad413c94'
    ])
