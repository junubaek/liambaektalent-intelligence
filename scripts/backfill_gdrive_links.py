import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import json
import urllib.parse
from connectors.notion_api import HeadhunterDB
from connectors.gdrive_api import GDriveConnector

# Define the local directories to scan for resumes
RESUME_DIRS = [
    r"C:\Users\cazam\Downloads\02_resume 전처리",
    r"C:\Users\cazam\Downloads\02_resume_converted_v8"
]

def find_local_file(candidate_name):
    # Walk through the directories and find the file matching the name or a likely combination
    # candidate_name is usually the '파일명' property in Notion like "CJ ENM_신사업_송선욱"
    for d in RESUME_DIRS:
        if not os.path.exists(d):
            continue
        for root, _, files in os.walk(d):
            for f in files:
                if f.startswith('~$') or f.startswith('.'):
                    continue
                # Exact name check (excluding extension)
                if os.path.splitext(f)[0] == candidate_name:
                    return os.path.join(root, f)
                # Flexible name check: if candidate "송선욱" is in title
                # Let's be strict first, then flexible if exact not found
    return None

def main():
    print("Initializing Google Drive Backfill Script...")
    db = HeadhunterDB()
    client = db.client
    
    with open("secrets.json", "r") as f:
        secrets = json.load(f)
        folder_id = secrets.get("GOOGLE_DRIVE_FOLDER_ID")
        
    if not folder_id:
        print("CRITICAL: GOOGLE_DRIVE_FOLDER_ID not found in secrets.json")
        return

    gdrive = GDriveConnector()
    print("GDrive Authenticated.")

    print("Fetching candidates from Notion...")
    # Fetch all candidates from Vector DB
    db_id = secrets.get("NOTION_DATABASE_ID")
    if not db_id:
         db_id = client.search_db_by_name("Vector DB")
         
    res = client.query_database(db_id, limit=None)
    pages = res.get('results', [])
    print(f"Found {len(pages)} overall pages in Notion DB.")

    success = 0
    skipped = 0
    not_found_local = 0

    for i, p in enumerate(pages):
        props = p.get('properties', {})
        page_id = p['id']
        
        # Get Candidate Name / File Name (Usually '파일명' or 'Name')
        title_prop = props.get("파일명") or props.get("Name") or props.get("임시 패턴명")
        if not title_prop or not title_prop.get("title"):
             continue
             
        name = title_prop["title"][0]["plain_text"]
        
        # Check current Google Drive Link
        url_prop = props.get("구글드라이브 링크")
        current_url = ""
        if url_prop and url_prop.get("url"):
             current_url = url_prop["url"]
             
        if current_url and "search?q=" not in current_url and "drive.google.com" in current_url:
             # Already a valid direct link
             skipped += 1
             continue
             
        print(f"[{i+1}/{len(pages)}] Processing: {name}")
        local_path = find_local_file(name)
        
        if not local_path:
             print(f"  -> [WARNING] Could not find local file for '{name}' in specified directories.")
             not_found_local += 1
             continue
             
        # Upload using GDriveConnector
        link = gdrive.upload_file_to_drive(local_path, folder_id, duplicate_check=True)
        if link:
             # Update Notion
             update_props = {
                 "구글드라이브 링크": {"url": link}
             }
             client.update_page_properties(page_id, update_props)
             print(f"  -> SUCCESS! Updated Notion with link: {link}")
             success += 1
        else:
             print(f"  -> [ERROR] Failed to upload to Google Drive.")

    print("-" * 50)
    print(f"Backfill Complete. Success: {success}, Skipped: {skipped}, Not found locally: {not_found_local}")

if __name__ == "__main__":
    main()
