import requests
import json
import os

with open("secrets.json", "r") as f:
    secrets = json.load(f)

NOTION_TOKEN = secrets["NOTION_API_KEY"]
NOTION_DB_ID = secrets["NOTION_DATABASE_ID"]

headers = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28"
}

def run_audit():
    print("🔍 Starting Final Data Integrity Audit...")
    url = f"https://api.notion.com/v1/databases/{NOTION_DB_ID}/query"
    
    all_pages = []
    has_more = True
    next_cursor = None
    
    while has_more:
        payload = {"page_size": 100}
        if next_cursor: payload["start_cursor"] = next_cursor
        
        resp = requests.post(url, headers=headers, json=payload).json()
        all_pages.extend(resp.get("results", []))
        has_more = resp.get("has_more", False)
        next_cursor = resp.get("next_cursor")
        print(f"  Loaded {len(all_pages)} pages...")

    total = len(all_pages)
    active_pages = [p for p in all_pages if not p.get("archived", False)]
    total_active = len(active_pages)
    
    blank_patterns = []
    blank_summary = []
    blank_sector = []
    missing_gdrive = []
    
    for p in active_pages:
        props = p["properties"]
        name_list = props.get("이름", {}).get("title", [])
        name = name_list[0].get("plain_text", "Unknown") if name_list else "Unknown"
        
        patterns = props.get("Experience Patterns", {}).get("multi_select", [])
        summary = props.get("경력 Summary", {}).get("rich_text", [])
        sector = props.get("Primary Sector", {}).get("multi_select", [])
        gdrive = props.get("구글드라이브 링크", {}).get("url")
        
        if not patterns:
            blank_patterns.append(name)
        if not summary:
            blank_summary.append(name)
        if not sector:
            blank_sector.append(name)
        if not gdrive:
            missing_gdrive.append(name)

    print("\n" + "="*40)
    print("📊 FINAL AUDIT RESULTS")
    print("="*40)
    print(f"Total Pages in DB: {total}")
    print(f"Total Active (Live): {total_active}")
    print(f"Archived Count: {total - total_active}")
    print("-" * 20)
    print(f"❌ Blank Experience Patterns: {len(blank_patterns)}")
    print(f"❌ Blank Career Summary: {len(blank_summary)}")
    print(f"❌ Blank Primary Sector: {len(blank_sector)}")
    print(f"⚠️ Missing GDrive Link: {len(missing_gdrive)}")
    print("-" * 20)
    
    if blank_patterns:
        print("\nList of Blank Patterns (Top 10):")
        for n in blank_patterns[:10]: print(f"  - {n}")
    
    if blank_sector:
        print("\nList of Blank Sector (Top 10):")
        for n in blank_sector[:10]: print(f"  - {n}")
    
    if len(blank_patterns) == 0 and len(blank_summary) == 0:
        print("\n✅ MISSION ACCOMPLISHED: Absolute Data Parity Achieved.")
    else:
        print("\n⚠️ ACTION REQUIRED: Data gaps still remain.")
    print("="*40)

if __name__ == "__main__":
    run_audit()
