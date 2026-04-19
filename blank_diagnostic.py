import json
import requests
import os

def diagnostic():
    with open('secrets.json', 'r') as f:
        secrets = json.load(f)
    
    NOTION_API_KEY = secrets['NOTION_API_KEY']
    DATABASE_ID = secrets['NOTION_DATABASE_ID']
    
    headers = {
        "Authorization": f"Bearer {NOTION_API_KEY}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28"
    }
    
    url = f"https://api.notion.com/v1/databases/{DATABASE_ID}/query"
    
    # 1. Get all blank entries
    blank_filter = {
        "or": [
            {"property": "Experience Patterns", "multi_select": {"is_empty": True}},
            {"property": "\uacbd\ub825 Summary", "rich_text": {"is_empty": True}}
        ]
    }
    
    blanks = []
    has_more = True
    next_cursor = None
    while has_more:
        payload = {"filter": blank_filter, "page_size": 100}
        if next_cursor: payload["start_cursor"] = next_cursor
        resp = requests.post(url, headers=headers, json=payload).json()
        results = resp.get("results", [])
        for r in results:
            if not r.get("archived"):
                name_list = r["properties"]["\uc774\ub984"]["title"]
                name = name_list[0]["plain_text"] if name_list else "Unknown"
                blanks.append({"name": name, "id": r["id"]})
        has_more = resp.get("has_more", False)
        next_cursor = resp.get("next_cursor")
    
    print(f"Total Blanks Found: {len(blanks)}")
    
    # 2. Check localized file repo
    DIR_RAW = r"C:\Users\cazam\Downloads\02_resume \uc804\ucd2a\ub9ac"
    DIR_CONV = r"C:\Users\cazam\Downloads\02_resume_converted_docx"
    all_files = []
    for d in [DIR_RAW, DIR_CONV]:
        if os.path.exists(d):
            all_files.extend([os.path.splitext(f)[0] for f in os.listdir(d)])
    
    print(f"Files in Repo: {len(all_files)}")
    
    match_count = 0
    missing_files = []
    for b in blanks:
        if b["name"] in all_files:
            match_count += 1
        else:
            # Fuzzy check?
            possible = [f for f in all_files if b["name"] in f]
            if possible:
                match_count += 1 # consider it a match for now
            else:
                missing_files.append(b["name"])
    
    print(f"Blanks with matching files: {match_count}")
    print(f"Blanks NO matching files: {len(missing_files)}")
    if missing_files:
        print(f"Sample missing filenames: {missing_files[:10]}")

if __name__ == "__main__":
    diagnostic()
