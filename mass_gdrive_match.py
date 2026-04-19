import os
import json
import sqlite3
import time
from connectors.gdrive_api import GDriveConnector

def main():
    print("Initiating Mass GDrive Match...")
    gdrive = GDriveConnector()
    
    conn = sqlite3.connect('candidates.db')
    c = conn.cursor()
    
    # Get remaining missing candidates
    query = """
    SELECT id, name_kr 
    FROM candidates 
    WHERE is_duplicate=0 
    AND (google_drive_url IS NULL OR google_drive_url='' OR google_drive_url='#')
    """
    targets = c.execute(query).fetchall()
    print(f"🎯 Total remaining missing candidates: {len(targets)}")
    
    found_links = {}
    used_file_ids = set()
    still_missing = []
    
    for idx, (cid, name) in enumerate(targets):
        if not name or name.strip() == "":
            still_missing.append((cid, "이름없음"))
            continue
            
        # Clean name for search (remove special chars if any)
        clean_name = name.strip()
        if len(clean_name) <= 1:
            still_missing.append((cid, clean_name))
            continue
            
        try:
            q = f"name contains '{clean_name}' and trashed = false and mimeType != 'application/vnd.google-apps.folder'"
            results = gdrive.service.files().list(
                q=q,
                fields="files(id, name, webViewLink)",
                spaces="drive"
            ).execute()
            
            files = results.get('files', [])
            available_files = [f for f in files if f.get('id') not in used_file_ids]
            
            if available_files:
                best_match = available_files[0]
                for f in available_files:
                    # prioritized match: exactly contains name
                    fname = f.get('name', '')
                    if clean_name in fname:
                        best_match = f
                        break
                        
                used_file_ids.add(best_match['id'])
                found_links[cid] = (clean_name, best_match['name'], best_match['webViewLink'])
                if len(found_links) % 10 == 0:
                    print(f"Matched {len(found_links)}... (latest: {clean_name} -> {best_match['name']})")
            else:
                still_missing.append((cid, clean_name))
        except Exception as e:
            print(f"Error searching for {clean_name}: {e}")
            still_missing.append((cid, clean_name))
            
        time.sleep(0.2) # Google API limit safety
        
    print(f"\n--- Mass Match Results ---")
    print(f"✅ Newly Found: {len(found_links)}")
    print(f"❌ Still Missing: {len(still_missing)}")
    
    if found_links:
        print("\n--- Updating SQLite ---")
        for cid, data in found_links.items():
            link = data[2]
            c.execute("UPDATE candidates SET google_drive_url = ? WHERE id = ?", (link, cid))
        conn.commit()
        
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
            print(f"JSON Update Error: {e}")

    conn.close()
    
    # Create Markdown artifact for still missing ones
    arti_path = r"C:\Users\cazam\.gemini\antigravity\brain\40516708-d2c8-4e50-a5f8-ff10183de737\artifacts\missing_final_list.md"
    os.makedirs(os.path.dirname(arti_path), exist_ok=True)
    
    doc = f"# 📄 최종 구글 드라이브(Docs) 누락 명단 ({len(still_missing)}명)\n\n"
    doc += "구글 드라이브 전수 스캔 및 Notion 페이지 백필 과정을 거치고도 최종적으로 이력서 첨부파일이 없는 후보자 명단입니다.\n"
    doc += "(이름 검색 결과 매칭되는 구글 드라이브 문서 없음)\n\n"
    doc += "| 연번 | 후보자 이름 | Notion ID |\n"
    doc += "|:---:|:---|:---|\n"
    
    for i, (cid, name) in enumerate(still_missing):
        doc += f"| {i+1} | {name} | `{cid}` |\n"
        
    with open(arti_path, 'w', encoding='utf-8') as f:
        f.write(doc)
        
    print("\n✨ Process Complete. Artifact generated.")

if __name__ == "__main__":
    main()
