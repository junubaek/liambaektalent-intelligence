import os
import json
import sqlite3
import re
import sys
sys.path.append(r"C:\Users\cazam\Downloads\이력서자동분석검색시스템")
sys.stdout.reconfigure(encoding='utf-8')
from connectors.gdrive_api import GDriveConnector

def extract_drive_id(url):
    if not url: return None
    m = re.search(r'/d/([a-zA-Z0-9_-]+)', url)
    if m: return m.group(1)
    m = re.search(r'id=([a-zA-Z0-9_-]+)', url)
    if m: return m.group(1)
    return None

def main():
    print("Initiating Auto Mapping of Orphan GDrive Files...")
    gdrive = GDriveConnector()
    
    conn = sqlite3.connect('candidates.db')
    c = conn.cursor()
    
    # 1. Get mapped Drive IDs from SQLite
    mapped_urls = c.execute("SELECT google_drive_url FROM candidates WHERE is_duplicate=0 AND google_drive_url IS NOT NULL AND google_drive_url != ''").fetchall()
    mapped_ids = set()
    for (url,) in mapped_urls:
        ext_id = extract_drive_id(url)
        if ext_id:
            mapped_ids.add(ext_id)
            
    print(f"Already mapped Drive IDs: {len(mapped_ids)}")
    
    # 2. Get unmapped candidates
    unmapped_cands = c.execute("SELECT id, name_kr, email, raw_text FROM candidates WHERE is_duplicate=0 AND (google_drive_url IS NULL OR google_drive_url='' OR google_drive_url='#')").fetchall()
    print(f"Unmapped Candidates in DB: {len(unmapped_cands)}")
    
    if not unmapped_cands:
        print("All candidates are already mapped!")
        conn.close()
        return
        
    # 3. Get all files from the designated Google Drive folder
    try:
        with open("secrets.json", "r", encoding="utf-8") as f:
            secrets = json.load(f)
        folder_id = secrets.get('GOOGLE_DRIVE_FOLDER_ID')
    except Exception as e:
        print(f"Failed to read secrets: {e}")
        conn.close()
        return
        
    if not folder_id:
        print("No GOOGLE_DRIVE_FOLDER_ID found in secrets.json")
        conn.close()
        return
        
    query = f"'{folder_id}' in parents and trashed=false and mimeType != 'application/vnd.google-apps.folder'"
    
    unmapped_files = []
    page_token = None
    while True:
        results = gdrive.service.files().list(
            q=query,
            fields="nextPageToken, files(id, name, webViewLink)",
            spaces="drive",
            pageToken=page_token
        ).execute()
        
        for file in results.get('files', []):
            if file['id'] not in mapped_ids:
                unmapped_files.append(file)
                
        page_token = results.get('nextPageToken')
        if not page_token:
            break
            
    print(f"Found {len(unmapped_files)} unmapped files in target Drive folder.")
    
    # 4. Attempt Matching heuristics and apply updates
    matches_count = 0
    used_drive_ids = set()
    
    for f in unmapped_files:
        fid = f['id']
        fname = f['name'].lower()
        clean_fname = re.sub(r'[\s_()\-0-9\.]', '', fname.replace('pdf','').replace('docx','').replace('doc','').replace('hwp',''))
        
        matched_cand_id = None
        matched_cand_name = None
        
        for cid, name, email, raw in unmapped_cands:
            cname = name.replace(" ", "").lower() if name else ""
            
            # heuristic 1: Cleaned Candidate name is in the filename
            # (Exclude very common generic terms like '원본', '이력서', 'resume', '백엔드' etc. to prevent false mappings)
            generic_words = {'원본', '이력서', 'resume', '백엔드', '개발자', '지원자', 'career', 'cv', '포지션'}
            if cname and cname not in generic_words and len(cname) >= 2 and cname in clean_fname:
                matched_cand_id = cid
                matched_cand_name = name
                break
                
            # heuristic 2: Email prefix match
            if email and email.split('@')[0].lower() in fname:
                matched_cand_id = cid
                matched_cand_name = name
                break
                
            # heuristic 3: Base filename in raw text
            base_fname = f['name'].rsplit('.', 1)[0]
            if raw and len(base_fname) > 5 and base_fname in raw:
                matched_cand_id = cid
                matched_cand_name = name
                break
                
        if matched_cand_id and fid not in used_drive_ids:
            used_drive_ids.add(fid)
            # Update SQLite immediately
            c.execute("UPDATE candidates SET google_drive_url = ? WHERE id = ?", (f['webViewLink'], matched_cand_id))
            matches_count += 1
            print(f"[{matches_count}] Matched: {f['name']} -> {matched_cand_name} ({matched_cand_id})")
            
    conn.commit()
    conn.close()
    
    print(f"\nAuto Mapping Complete! Successfully linked {matches_count} candidates to their Google Drive CV files.")

if __name__ == "__main__":
    main()
