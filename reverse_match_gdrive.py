import os
import json
import sqlite3
import re
from connectors.gdrive_api import GDriveConnector

def extract_drive_id(url):
    if not url: return None
    # match /d/ID/ or ?id=ID
    m = re.search(r'/d/([a-zA-Z0-9_-]+)', url)
    if m: return m.group(1)
    m = re.search(r'id=([a-zA-Z0-9_-]+)', url)
    if m: return m.group(1)
    return None

def main():
    print("Initiating Reverse Match Analysis...")
    gdrive = GDriveConnector()
    
    # 1. Get mapped Drive IDs from SQLite
    conn = sqlite3.connect('candidates.db')
    c = conn.cursor()
    
    mapped_urls = c.execute("SELECT google_drive_url FROM candidates WHERE is_duplicate=0 AND google_drive_url IS NOT NULL AND google_drive_url != ''").fetchall()
    mapped_ids = set()
    for (url,) in mapped_urls:
        ext_id = extract_drive_id(url)
        if ext_id:
            mapped_ids.add(ext_id)
            
    print(f"Mapped {len(mapped_ids)} unique Drive File IDs from DB.")
    
    # 2. Get unmapped Candidates
    unmapped_cands = c.execute("SELECT id, name_kr, email, raw_text FROM candidates WHERE is_duplicate=0 AND (google_drive_url IS NULL OR google_drive_url='' OR google_drive_url='#')").fetchall()
    print(f"Unmapped Candidates: {len(unmapped_cands)}")
    
    # 3. Get all files in the designated folder
    try:
        with open("secrets.json", "r") as f:
            secrets = json.load(f)
        folder_id = secrets.get('GOOGLE_DRIVE_FOLDER_ID')
    except:
        folder_id = None
        
    if not folder_id:
        print("No Folder ID found.")
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
            
    print(f"Found {len(unmapped_files)} files in the target Drive folder that are NOT mapped to any candidate.")

    # 4. Attempt Matching heuristics
    matches = []
    
    for f in unmapped_files:
        fname = f['name'].lower()
        clean_fname = re.sub(r'[\s_()\-0-9\.]', '', fname.replace('pdf','').replace('docx','').replace('doc','').replace('hwp',''))
        
        matched_cand = None
        for cid, name, email, raw in unmapped_cands:
            cname = name.replace(" ", "").lower() if name else ""
            
            # heuristic 1: Cleaned Candidate name is in the filename
            if cname and len(cname) >= 2 and cname in clean_fname:
                matched_cand = (cid, name, "Name substring match")
                break
                
            # heuristic 2: Email in filename (rare but possible)
            if email and email.split('@')[0].lower() in fname:
                matched_cand = (cid, name, "Email prefix match")
                break
                
            # heuristic 3: Base filename in raw text (without extension)
            base_fname = f['name'].rsplit('.', 1)[0]
            if raw and len(base_fname)>3 and base_fname in raw:
                matched_cand = (cid, name, "Filename in raw text")
                break
                
        if matched_cand:
            matches.append((f, matched_cand))
            
    # Write to Markdown Artifact
    arti_path = r"C:\Users\cazam\.gemini\antigravity\brain\40516708-d2c8-4e50-a5f8-ff10183de737\artifacts\reverse_match_analysis.md"
    os.makedirs(os.path.dirname(arti_path), exist_ok=True)
    
    doc = f"# 🔍 미아 파일(Orphan Files) 역추적 매칭 분석\n\n"
    doc += f"- 이력서 폴더 내 전체 미매핑 파일 수: **{len(unmapped_files)}개**\n"
    doc += f"- 잔여 누락 후보자 수: **{len(unmapped_cands)}명**\n"
    doc += f"- 매칭 예상 건수: **{len(matches)}건**\n\n"
    
    doc += "## 🎯 유력 매칭 후보 (자동 분석 결과 자동 추론)\n"
    doc += "| 파일명 | 예상 후보자 이름 | 매칭 사유 | 후보자 ID |\n"
    doc += "|---|---|---|---|\n"
    for f, (cid, name, reason) in matches:
        doc += f"| [{f['name']}]({f['webViewLink']}) | **{name}** | {reason} | `{cid}` |\n"
        
    doc += "\n## 📁 드라이브에 불시착한 나머지 파일들 (매칭 실패)\n"
    doc += "후보자 이름이나 정보와 전혀 매칭되지 않는 파일들입니다.\n\n"
    matched_fids = set([f['id'] for f, _ in matches])
    unmatched_clean = [f for f in unmapped_files if f['id'] not in matched_fids]
    
    doc += "| 파일명 | 링크 |\n"
    doc += "|---|---|\n"
    for f in unmatched_clean:
         doc += f"| {f['name']} | [열기]({f['webViewLink']}) |\n"

    with open(arti_path, "w", encoding="utf-8") as file:
        file.write(doc)
        
    print("\n✨ Reverse matching complete. Artifact generated.")
    
if __name__ == "__main__":
    main()
