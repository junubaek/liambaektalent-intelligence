import os
import json
import time
import urllib.parse
from connectors.notion_api import HeadhunterDB
import PyPDF2
from docx import Document
import win32com.client
import pythoncom
from connectors.gdrive_api import GDriveConnector

RESUME_DIR = r"C:\Users\cazam\Downloads\02_resume 전처리"

def chunk_text(text, limit=1000):
    return [text[i:i+limit] for i in range(0, len(text), limit)]

def extract_text_from_pdf(filepath):
    text = ""
    try:
        with open(filepath, 'rb') as f:
            reader = PyPDF2.PdfReader(f)
            for page in reader.pages:
                extracted = page.extract_text()
                if extracted:
                    text += extracted + "\n"
    except Exception as e:
        print(f"Error reading PDF {filepath}: {e}")
    return text

def extract_text_from_doc_using_win32(file_path):
    try:
        pythoncom.CoInitialize()
        word = win32com.client.Dispatch("Word.Application")
        word.Visible = False
        word.DisplayAlerts = False
        abs_path = os.path.abspath(file_path)
        doc = word.Documents.Open(abs_path)
        text = doc.Range().Text
        doc.Close()
        word.Quit()
        return text
    except Exception as e:
        print(f"Error reading Word file {file_path}: {e}")
        return ""

def extract_text_from_docx(file_path):
    try:
        doc = Document(file_path)
        text = []
        for para in doc.paragraphs:
            text.append(para.text)
        return '\n'.join(text)
    except Exception as e:
        print(f"Error reading DOCX {file_path}: {e}")
        return ""

def extract_text(file_path):
    ext = os.path.splitext(file_path)[1].lower()
    if ext == '.pdf':
        return extract_text_from_pdf(file_path)
    elif ext == '.docx':
        return extract_text_from_docx(file_path)
    elif ext == '.doc':
        return extract_text_from_doc_using_win32(file_path)
    return ""

def main():
    print("Initializing Incremental Notion Uploader...")
    db = HeadhunterDB()
    client = db.client
    
    target_db_name = "Vector DB"
    db_id = None
    try:
        with open("secrets.json", "r") as f:
            secrets = json.load(f)
            db_id = secrets.get("NOTION_DATABASE_ID")
    except Exception:
        pass
        
    if not db_id:
        db_id = client.search_db_by_name(target_db_name)
    
    if not db_id:
        print(f"CRITICAL: Database '{target_db_name}' not found!")
        return

    print(f"Found Target DB: {target_db_name} ({db_id})")
    
    print("Fetching existing pages to map titles to IDs...")
    existing_pages = {}
    
    res = client.query_database(db_id, limit=None)
    all_results = res.get('results', [])
    
    for p in all_results:
        props = p.get('properties', {})
        for key, val in props.items():
            if val['type'] == 'title':
                if val['title']:
                    title = val['title'][0]['plain_text']
                    existing_pages[title] = p['id']
    
    print(f"Found {len(existing_pages)} unique existing titles.")

    files = []
    print(f"Scanning {RESUME_DIR} based on preflight_unique.json...")
    
    unique_names = set()
    try:
        if os.path.exists("preflight_unique.json"):
            with open("preflight_unique.json", "r", encoding="utf-8") as f:
                unique_list = json.load(f)
                unique_names = set(unique_list)
            print(f"Loaded {len(unique_names)} unique names from preflight_unique.json")
    except Exception as e:
        print("Could not load preflight_unique.json. Falling back to all files.")
        
    for root, dirs, filenames in os.walk(RESUME_DIR):
        for f in filenames:
             if f.startswith('~$') or f.startswith('.'):
                 continue
             if f.lower().endswith(('.pdf', '.docx', '.doc')):
                 name_check = os.path.splitext(f)[0]
                 filepath = os.path.join(root, f)
                 
                 # Only add if it's in the unique_names (deduplicated) list
                 if not unique_names or name_check in unique_names:
                     files.append(filepath)

    print(f"Found {len(files)} UNIQUE resume files for upload.")
    
    success_count = 0
    fail_count = 0
    skipped_count = 0
    
    for i, filepath in enumerate(files):
        filename = os.path.basename(filepath)
        name_check = os.path.splitext(filename)[0]
        
        print(f"[{i+1}/{len(files)}] Processing: {filename}...")
        
        # Notion title check (secondary fail-safe)
        if name_check in existing_pages:
             print(f"  -> File '{name_check}' already in Notion DB (by title). Skipping.")
             skipped_count += 1
             continue
        
        # Extract Text
        content = extract_text(filepath)
            
        if not content.strip():
            print(f"  [!] No text extracted. Uploading with placeholder.")
            content = "Original File Content Not Extracted. Please check the attached link."
            
        name_prop = os.path.splitext(filename)[0]
        
        # --- NEW: Upload to Google Drive directly ---
        drive_link = ""
        try:
            with open("secrets.json", "r") as f:
                sec = json.load(f)
                folder_id = sec.get("GOOGLE_DRIVE_FOLDER_ID")
                
            if folder_id:
                # instantiate connector locally since it's lazy logic over loop
                gdrive = GDriveConnector()
                link = gdrive.upload_file_to_drive(filepath, folder_id, duplicate_check=True)
                if link:
                    drive_link = link
        except Exception as e:
            print(f"Error initiating GDrive upload: {e}")
            
        # Fallback to search query if upload failed or not configured
        if not drive_link:
            drive_link = f"https://drive.google.com/drive/u/0/search?q={urllib.parse.quote(filename)}"
        # --------------------------------------------
        
        children_blocks = []
        children_blocks.append({
            "object": "block",
            "type": "callout",
            "callout": {
                "rich_text": [{"type": "text", "text": { "content": f"📂 View Original File: {filename}", "link": {"url": drive_link} }}],
                "icon": {"emoji": "📄"}
            }
        })

        chunks = chunk_text(content)
        if len(chunks) > 50:
             chunks = chunks[:50]
             chunks.append("... (Truncated)")
             
        for chunk in chunks:
            children_blocks.append({
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [{ "type": "text", "text": { "content": chunk } }]
                }
            })
            
        properties = {
            "파일명": {"title": [{"text": {"content": name_prop}}]},
            "구글드라이브 링크": {"url": drive_link}
        }

        try:
            res = client.create_page(db_id, properties, children_blocks)
            if res:
                print("  -> Upload Success!")
                success_count += 1
            else:
                print("  -> Upload Failed (API Error).")
                fail_count += 1
        except Exception as e:
            print(f"  -> Upload Failed: {e}")
            fail_count += 1
            
        time.sleep(0.5)

    print("\n" + "="*30)
    print(f"Upload Complete. Success: {success_count}, Failed: {fail_count}, Skipped: {skipped_count}")

if __name__ == "__main__":
    main()
