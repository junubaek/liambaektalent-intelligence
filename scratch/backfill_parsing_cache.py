import sqlite3
import json
import datetime

def backfill_parsing_cache():
    conn = sqlite3.connect('candidates.db')
    cur = conn.cursor()
    
    # Get all master candidates without a parsing_cache record
    cur.execute('''
        SELECT c.id, c.name_kr, c.email, c.phone, c.birth_year, c.total_years, 
               c.sector, c.profile_summary, c.current_company, c.careers_json, 
               c.education_json, c.google_drive_url, c.source_file
        FROM candidates c
        LEFT JOIN parsing_cache pc ON c.id = pc.candidate_id
        WHERE c.is_duplicate=0 AND pc.candidate_id IS NULL
    ''')
    rows = cur.fetchall()
    print(f"Total candidates to backfill: {len(rows)}")
    
    backfilled_count = 0
    now_str = datetime.datetime.utcnow().isoformat()
    
    # We will do bulk inserts inside a transaction
    for r in rows:
        cid, name_kr, email, phone, birth_year, total_years, sector, profile_summary, current_company, careers_json, education_json, google_drive_url, source_file = r
        
        # Safely parse JSON strings
        try:
            careers_list = json.loads(careers_json) if careers_json else []
        except:
            careers_list = []
            
        try:
            education_list = json.loads(education_json) if education_json else []
        except:
            education_list = []
            
        parsed_dict = {
            "name": name_kr,
            "name_kr": name_kr,
            "email": email or "",
            "phone": phone or "",
            "birth_year": birth_year,
            "total_years": total_years or 0.0,
            "sector": sector or "미분류",
            "main_sectors": [sector] if sector and sector != "미분류" else [],
            "sub_sectors": [],
            "profile_summary": profile_summary or "",
            "current_company": current_company or "미지정",
            "careers": careers_list,
            "parsed_career_json": careers_list,
            "education": education_list,
            "google_drive_url": google_drive_url or "",
            "source_file": source_file or ""
        }
        
        parsed_json_str = json.dumps(parsed_dict, ensure_ascii=False)
        
        cur.execute('''
            INSERT INTO parsing_cache (candidate_id, prompt_version, logic_hash, parsed_json, updated_at)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            cid, 
            'v8.5_20260406', 
            '3861537bded03d1bfbebeecdc47febb717a185249d7396f58b8404f6bb833985', 
            parsed_json_str, 
            now_str
        ))
        backfilled_count += 1
        
    conn.commit()
    conn.close()
    print(f"Successfully backfilled {backfilled_count} candidate records into parsing_cache!")

if __name__ == "__main__":
    backfill_parsing_cache()
