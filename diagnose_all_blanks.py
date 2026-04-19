
import os
import json
import sys
import requests

PROJECT_ROOT = r"C:\Users\cazam\Downloads\이력서자동분석검색시스템"
sys.path.append(PROJECT_ROOT)

with open(os.path.join(PROJECT_ROOT, "secrets.json"), "r") as f:
    secrets = json.load(f)

NOTION_TOKEN = secrets["NOTION_API_KEY"]
NOTION_DB_ID = secrets["NOTION_DATABASE_ID"]

headers = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28"
}

def find_all_blanks():
    url = f"https://api.notion.com/v1/databases/{NOTION_DB_ID}/query"
    
    incomplete_candidates = []
    has_more = True
    next_cursor = None
    
    while has_more:
        payload = {"page_size": 100}
        if next_cursor: payload["start_cursor"] = next_cursor
        
        resp = requests.post(url, headers=headers, json=payload).json()
        results = resp.get('results', [])
        
        for r in results:
            if r.get('archived'): continue
            props = r['properties']
            name_list = props.get('이름', {}).get('title', [])
            name = name_list[0]['plain_text'] if name_list else "Unknown"
            
            exp_summary = "".join([t['plain_text'] for t in props.get('Experience Summary', {}).get('rich_text', [])])
            main_sectors = props.get('Main Sectors', {}).get('multi_select', [])
            sub_sectors = props.get('Sub Sectors', {}).get('multi_select', [])
            
            is_incomplete = "incomplete" in exp_summary.lower() or "missing" in exp_summary.lower() or "sparse" in exp_summary.lower()
            is_blank = not main_sectors or not sub_sectors or not exp_summary
            
            if is_incomplete or is_blank:
                incomplete_candidates.append({
                    "id": r['id'],
                    "name": name,
                    "reason": "Incomplete Message" if is_incomplete else "Missing Fields"
                })
                
        has_more = resp.get('has_more', False)
        next_cursor = resp.get('next_cursor')

    print(f"Total Incomplete/Blank candidates found: {len(incomplete_candidates)}")
    print(json.dumps(incomplete_candidates[:50], indent=2, ensure_ascii=False)) # Show first 50
    
    with open("incomplete_list.json", "w", encoding="utf-8") as f:
        json.dump(incomplete_candidates, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    find_all_blanks()
