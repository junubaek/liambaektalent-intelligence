import os
import json
import re
from tqdm import tqdm
from connectors.notion_api import HeadhunterDB
import fitz
from docx import Document

FOLDER1 = r"C:\Users\cazam\Downloads\02_resume 전처리"
FOLDER2 = r"C:\Users\cazam\Downloads\02_resume_converted_docx"
FOLDER3 = r"C:\Users\cazam\Downloads\02_resume_converted_v8"

def collect_files():
    files = {}
    for folder in [FOLDER1, FOLDER2, FOLDER3]:
        if os.path.exists(folder):
            for f in os.listdir(folder):
                if f.endswith((".pdf", ".docx", ".doc")):
                    base_name = f.rsplit(".", 1)[0]
                    if base_name not in files:
                        files[base_name] = os.path.join(folder, f)
    return files

def extract_text(filepath):
    ext = filepath.rsplit(".", 1)[-1].lower()
    try:
        if ext == "pdf":
            doc = fitz.open(filepath)
            return "\n".join(page.get_text() for page in doc)
        elif ext in ("docx", "doc"):
            doc = Document(filepath)
            return "\n".join(p.text for p in doc.paragraphs)
    except Exception as e:
        pass
    return ""

def extract_phone(text):
    match = re.search(r'010[- .]?\d{4}[- .]?\d{4}', text)
    return match.group(0) if match else ""

def extract_email(text):
    match = re.search(r'[\w.-]+@[\w.-]+\.\w+', text)
    return match.group(0) if match else ""

def main():
    print("Fetching existing candidates from Notion...")
    db = HeadhunterDB('secrets.json') # Connect to Notion API using HeadhunterDB wrapper
    client = db.client

    # Get the target database ID
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

    res = client.query_database(db_id, limit=None)
    pages = res.get('results', [])
    
    print(f"Found {len(pages)} pages in Notion DB. Extracting mapping...")

    # Map filename to page_id, and check existing fields
    page_map = {}
    for p in pages:
        props = p.get('properties', {})
        # Find Title Property (파일명 vs Name depending on schema, usually title is "파일명" in previous scripts)
        title_prop = None
        for k, v in props.items():
            if v.get('type') == 'title':
                title_prop = v['title']
                break
                
        if title_prop:
            title = "".join(t.get("plain_text", "") for t in title_prop)
            page_map[title] = {
                "id": p['id'],
                "has_phone": bool(props.get("전화번호", {}).get("phone_number")),
                "has_email": bool(props.get("이메일", {}).get("email"))
            }

    print("Locating local physical files...")
    files = collect_files()
    print(f"Found {len(files)} files locally.")

    match_count = 0
    updated_count = 0
    
    # Track statistics
    total_phones = 0
    total_emails = 0

    from concurrent.futures import ThreadPoolExecutor, as_completed
    
    def patch_candidate(name, filepath, info):
        # Skip extract if already has both
        if info["has_phone"] and info["has_email"]:
            return name, False, 0, 0
            
        text = extract_text(filepath)
        phone = extract_phone(text)
        email = extract_email(text)
        
        patch_props = {}
        phones_added = 0
        emails_added = 0
        
        if phone and not info["has_phone"]:
            patch_props["전화번호"] = {"phone_number": phone}
            phones_added = 1
        if email and not info["has_email"]:
            patch_props["이메일"] = {"email": email}
            emails_added = 1
            
        if patch_props:
            try:
                url = f"https://api.notion.com/v1/pages/{info['id']}"
                headers = {
                    "Authorization": f"Bearer {secrets.get('NOTION_API_KEY')}",
                    "Notion-Version": "2022-06-28",
                    "Content-Type": "application/json"
                }
                data = {"properties": patch_props}
                import requests
                resp = requests.patch(url, headers=headers, json=data)
                if resp.status_code == 200:
                    return name, True, phones_added, emails_added
            except Exception as e:
                pass
        return name, False, 0, 0

    tasks = []
    with ThreadPoolExecutor(max_workers=20) as executor:
        for name, filepath in files.items():
            if name in page_map:
                match_count += 1
                tasks.append(executor.submit(patch_candidate, name, filepath, page_map[name]))
                
        for future in tqdm(as_completed(tasks), total=len(tasks), desc="Patching Contacts (Concurrent)"):
            name, updated, p_added, e_added = future.result()
            if updated:
                updated_count += 1
                total_phones += p_added
                total_emails += e_added

    print(f"✅ Contact sync operation completed.")
    print(f"Matched PDF files to Notion records: {match_count}")
    print(f"Notion Nodes Updated: {updated_count}")
    print(f"Total Phones Extracted & Cleanly Pushed: {total_phones}")
    print(f"Total Emails Extracted & Cleanly Pushed: {total_emails}")

    with open("sync_notion_contacts_result.json", "w") as f:
        json.dump({"updated": updated_count, "phones": total_phones, "emails": total_emails}, f)

if __name__ == "__main__":
    main()
