import os
import json
import sqlite3
import time
from connectors.gdrive_api import GDriveConnector
from googleapiclient.http import MediaFileUpload

def get_drive_folder_id():
    with open("secrets.json", "r") as f:
        secrets = json.load(f)
    return secrets.get('GOOGLE_DRIVE_FOLDER_ID')

def main():
    print("Initiating Local -> Google Drive Match & Upload (Excluding Portfolio)...")
    folder_id = get_drive_folder_id()
    if not folder_id:
        print("Error: GOOGLE_DRIVE_FOLDER_ID not found in secrets.json")
        return

    gdrive = GDriveConnector()
    print("Google Drive Auth Success.")

    # 1. Fetch missing candidates
    conn = sqlite3.connect('candidates.db')
    c = conn.cursor()
    query = """
    SELECT id, name_kr 
    FROM candidates 
    WHERE is_duplicate=0 
    AND (google_drive_url IS NULL OR google_drive_url='' OR google_drive_url='#')
    """
    targets = c.execute(query).fetchall()
    print(f"🎯 Total remaining missing candidates: {len(targets)}")

    # 2. Scan Local Paths
    p1 = r'C:\Users\cazam\Downloads\02_resume 전처리'
    p2 = r'C:\Users\cazam\Downloads\02_resume_converted_v8'
    
    local_files = [] # list of dicts: {'name': filename, 'path': fullpath, 'prio': 1 or 2}
    
    def scan_dir(dir_path, priority):
        if not os.path.exists(dir_path): return
        for fname in os.listdir(dir_path):
            if os.path.isfile(os.path.join(dir_path, fname)):
                local_files.append({'name': fname, 'path': os.path.join(dir_path, fname), 'prio': priority})

    scan_dir(p1, 1)
    scan_dir(p2, 2)
    print(f"Scanned {len(local_files)} files locally.")

    found_links = {}
    still_missing = []
    new_uploads = 0

    for cid, name in targets:
        if not name or name.strip() == "" or len(name.strip()) < 2:
            still_missing.append((cid, name if name else "이름없음"))
            continue
            
        cname = name.strip()
        
        # Heuristic Matching in local files
        matches = []
        for lf in local_files:
            if cname in lf['name']:
                matches.append(lf)
                
        # Filter out Portfolios
        filtered_matches = [m for m in matches if '포트폴리오' not in m['name'] and 'portfolio' not in m['name'].lower()]
        
        if not filtered_matches:
            still_missing.append((cid, cname))
            continue
            
        # Sort by priority, then shortest length (to prevent accidental huge bundled filenames)
        filtered_matches.sort(key=lambda x: (x['prio'], len(x['name'])))
        best_match = filtered_matches[0]
        local_path = best_match['path']
        filename = best_match['name']
        
        # Check if already exists in Drive exactly
        try:
            query_str = f"name = '{filename}' and '{folder_id}' in parents and trashed = false"
            res = gdrive.service.files().list(q=query_str, fields="files(id, name, webViewLink)", spaces="drive").execute()
            
            drive_files = res.get('files', [])
            if drive_files:
                # File already exists
                link = drive_files[0]['webViewLink']
                found_links[cid] = (cname, filename, link, 'Already Uploaded')
            else:
                # Upload to Google Drive as requested
                print(f"Uploading {filename} to Google Drive...")
                file_metadata = {
                    'name': filename,
                    'parents': [folder_id]
                }
                # Determine mimeType based on extension for basic cases
                ext = filename.lower().split('.')[-1]
                mimeType = 'application/octet-stream'
                if ext == 'pdf': mimeType = 'application/pdf'
                elif ext == 'doc': mimeType = 'application/msword'
                elif ext == 'docx': mimeType = 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
                elif ext == 'hwp': mimeType = 'application/x-hwp'
                
                media = MediaFileUpload(local_path, mimetype=mimeType, resumable=True)
                uploaded_file = gdrive.service.files().create(
                    body=file_metadata,
                    media_body=media,
                    fields='id, webViewLink'
                ).execute()
                
                link = uploaded_file.get('webViewLink')
                found_links[cid] = (cname, filename, link, 'Newly Uploaded')
                new_uploads += 1
                
        except Exception as e:
            print(f"Error handling Drive for {cname} ({filename}): {e}")
            still_missing.append((cid, cname))
            continue
            
    print(f"\n--- Result ---")
    print(f"✅ Total Matched (Local): {len(found_links)}")
    print(f"⬆️ New Uploads to Drive: {new_uploads}")
    print(f"❌ Still Unmatched: {len(still_missing)}")

    # Update SQLite Database
    print("\n--- Updating SQLite Database ---")
    for cid, data in found_links.items():
        c.execute("UPDATE candidates SET google_drive_url = ? WHERE id = ?", (data[2], cid))
    conn.commit()
    conn.close()
    
    # Update JSON Cache
    print("--- Updating JSON Cache ---")
    try:
        with open('candidates_cache_jd.json', 'r', encoding='utf-8') as f:
            cache = json.load(f)
            
        for cand in cache:
            cid = cand.get('id')
            if cid in found_links:
                cand['google_drive_url'] = found_links[cid][2]
                
        with open('candidates_cache_jd.json', 'w', encoding='utf-8') as f:
            json.dump(cache, f, ensure_ascii=False, indent=2)
        print("JSON Cache Updated.")
    except Exception as e:
        print(f"JSON Cache Update Failed: {e}")

    # Generate final Missing List
    arti_path = r"C:\Users\cazam\.gemini\antigravity\brain\40516708-d2c8-4e50-a5f8-ff10183de737\artifacts\final_unmatched_172_result.md"
    os.makedirs(os.path.dirname(arti_path), exist_ok=True)
    doc = f"# 📄 최종 남은 로컬/클라우드 누락 명단 ({len(still_missing)}명)\n\n"
    doc += "구글 드라이브, 로컬 폴더(02_resume 전처리, 02_resume_converted_v8)를 전수 탐색하고 포트폴리오를 제외한 매칭에서도 전혀 원본 이력서 파일을 발견하지 못한 명단입니다.\n\n"
    doc += "| 연번 | 이름 | Notion ID |\n|---|---|---|\n"
    for i, (cid, name) in enumerate(still_missing):
        doc += f"| {i+1} | {name} | `{cid}` |\n"
    
    with open(arti_path, 'w', encoding='utf-8') as f:
        f.write(doc)
    
    print("\n✨ Process Complete!")

if __name__ == "__main__":
    main()
