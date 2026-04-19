import os
import json
import sqlite3
from connectors.gdrive_api import GDriveConnector
from googleapiclient.http import MediaFileUpload

def get_drive_folder_id():
    with open("secrets.json", "r") as f:
        return json.load(f).get('GOOGLE_DRIVE_FOLDER_ID')

def fix_two_candidates():
    print("--- Fixing Jaden Lim & 백병남 ---")
    conn = sqlite3.connect('candidates.db')
    c = conn.cursor()
    gdrive = GDriveConnector()
    folder_id = get_drive_folder_id()
    
    fixes = [
        # (ID, old_name_kr, new_name_kr, local_filename)
        ("07d757af-80b0-4b78-b6c2-982d8f60476a", "Jaden Jaehyun Lim", "임재현", "RESUME_Jaehyun Jaden Lim 2020.pdf"),
        ("624df6d4-13de-4bcd-8bf3-6e3bf3300cf2", "백 병 남", "백병남", "[Java backend]백병남 개발자.docx")
    ]
    
    found_links = {}
    base_dir = r'C:\Users\cazam\Downloads\02_resume 전처리'
    
    for cid, old_name, new_name, fname in fixes:
        local_path = os.path.join(base_dir, fname)
        if not os.path.exists(local_path):
            print(f"File not found: {local_path}")
            continue
            
        print(f"Uploading {fname} for {new_name}...")
        try:
            # Check if exists in drive
            res = gdrive.service.files().list(q=f"name='{fname}' and '{folder_id}' in parents and trashed=false", fields="files(id, webViewLink)").execute()
            if res.get('files'):
                link = res['files'][0]['webViewLink']
            else:
                mime_type = 'application/pdf' if fname.endswith('.pdf') else 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
                media = MediaFileUpload(local_path, mimetype=mime_type, resumable=True)
                uploaded = gdrive.service.files().create(
                    body={'name': fname, 'parents': [folder_id]},
                    media_body=media, fields='id, webViewLink').execute()
                link = uploaded.get('webViewLink')
                
            found_links[cid] = link
            # Update DB with new name
            c.execute("UPDATE candidates SET name_kr = ?, google_drive_url = ? WHERE id = ?", (new_name, link, cid))
            print(f"✅ {new_name} DB Updated")
        except Exception as e:
            print(f"Error uploading {fname}: {e}")
            
    conn.commit()
    conn.close()
    
    if found_links:
        try:
            with open('candidates_cache_jd.json', 'r', encoding='utf-8') as f:
                cache = json.load(f)
            for cand in cache:
                if cand.get('id') in found_links:
                    match = next(x for x in fixes if x[0] == cand.get('id'))
                    cand['name_kr'] = match[2]
                    cand['name'] = match[2]
                    cand['google_drive_url'] = found_links[cand.get('id')]
            with open('candidates_cache_jd.json', 'w', encoding='utf-8') as f:
                json.dump(cache, f, ensure_ascii=False, indent=2)
            print("✅ JSON Cache Updated")
        except Exception as e:
            print(f"JSON Update error: {e}")

def scan_unparsed():
    print("\n--- Scanning Unparsed Files in 02_resume 전처리 ---")
    base_dir = r'C:\Users\cazam\Downloads\02_resume 전처리'
    if not os.path.exists(base_dir): return
    
    conn = sqlite3.connect('candidates.db')
    # Get all names >= 2 chars, exclude garbage
    cands = conn.execute("SELECT name_kr FROM candidates WHERE is_duplicate=0 AND name_kr IS NOT NULL").fetchall()
    valid_names = set(c[0].strip().replace(" ", "") for c in cands if len(c[0].strip()) >= 2)
    conn.close()
    
    local_files = os.listdir(base_dir)
    unparsed = []
    
    for f in local_files:
        clean_f = f.replace(" ", "")
        matched = False
        for n in valid_names:
            if n in clean_f:
                matched = True
                break
        
        if not matched:
            unparsed.append(f)
            
    arti_path = r"C:\Users\cazam\.gemini\antigravity\brain\40516708-d2c8-4e50-a5f8-ff10183de737\artifacts\unparsed_resumes.md"
    doc = f"# 📁 아직 파싱/업로드되지 않은 로컬 파일 리스트\n\n"
    doc += f"- 검색 위치: `{base_dir}`\n"
    doc += f"- 전체 수량 중 미파싱 예상 수량: **{len(unparsed)}개**\n"
    doc += "(DB에 등록된 어떠한 후보자 이름도 파일명에 포함되어 있지 않은 파일들입니다.)\n\n"
    doc += "| 연번 | 파일명 |\n|---|---|\n"
    
    for i, f in enumerate(unparsed):
        doc += f"| {i+1} | {f} |\n"
        
    with open(arti_path, 'w', encoding='utf-8') as f:
        f.write(doc)
    print(f"✨ Found {len(unparsed)} unmatched files. Artifact created.")

if __name__ == "__main__":
    fix_two_candidates()
    scan_unparsed()
