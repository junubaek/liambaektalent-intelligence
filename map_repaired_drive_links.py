import os
import json
import sqlite3
from connectors.gdrive_api import GDriveConnector

def main():
    print("Connecting to Google Drive...")
    gdrive = GDriveConnector()
    
    updates = [
        ("33522567-1b6f-81d1-84b4-d80fff34b631", "김보람"),
        ("69832170-515b-40b6-95f4-65de96656665", "어울림"),
        ("2d65303e-0fff-4868-924c-11f699a577c1", "이상열"),
        ("2c6aba15-67ed-4c11-a251-e3d7c59d1247", "정한아"),
        ("8147a5d5-85b3-409e-b120-ea5ac64a5e14", "최종요"),
        ("fc659206-ef0e-4cbe-bac3-17bd665f4df1", "최종호"),
        ("25dd9a02-b5ac-4838-92a3-0fa886853099", "홍승언"),
        ("3f64bc68-eda8-4ca7-894c-3a16d58a7ba8", "강한")
    ]
    
    found_links = {}
    used_file_ids = set() # To ensure 1-to-1 strict mapping
    
    print("\n--- Searching Google Drive ---")
    for cid, name in updates:
        # Search by exact or partial name in filename
        query = f"name contains '{name}' and trashed = false and mimeType != 'application/vnd.google-apps.folder'"
        results = gdrive.service.files().list(
            q=query,
            fields="files(id, name, webViewLink)",
            spaces="drive"
        ).execute()
        
        files = results.get('files', [])
        
        # Avoid already assigned files
        available_files = [f for f in files if f.get('id') not in used_file_ids]
        
        if available_files:
            # Pick the first one that matches
            best_match = available_files[0]
            for f in available_files:
                # If exact name match, prioritize it
                if name in f.get('name', '') and name == f.get('name', '').replace('.pdf', '').replace('.doc', '').replace('.docx', ''):
                    best_match = f
                    break
            
            used_file_ids.add(best_match['id'])
            found_links[cid] = (name, best_match['name'], best_match['webViewLink'])
            print(f"✅ {name}: Found -> {best_match['name']} ({best_match['webViewLink']})")
        else:
            print(f"❌ {name}: No file found in Drive")
            
    print("\n--- Updating SQLite Database ---")
    conn = sqlite3.connect('candidates.db')
    c = conn.cursor()
    for cid, data in found_links.items():
        _, _, link = data
        c.execute("UPDATE candidates SET google_drive_url = ? WHERE id = ?", (link, cid))
    conn.commit()
    conn.close()
    print("SQLite Updated.")
    
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
        
    print("\n✨ Process Complete!")

if __name__ == "__main__":
    main()
