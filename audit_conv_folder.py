
import os
import json
import sys

PROJECT_ROOT = r"C:\Users\cazam\Downloads\이력서자동분석검색시스템"
sys.path.append(PROJECT_ROOT)

from connectors.notion_api import NotionClient

DIR_CONV = r"C:\Users\cazam\Downloads\02_resume_converted_docx"

def audit_conv():
    with open("secrets.json", "r") as f:
        secrets = json.load(f)
    
    notion_client = NotionClient(secrets["NOTION_API_KEY"])
    notion_db_id = secrets.get("NOTION_DATABASE_ID")

    files = [os.path.splitext(f)[0] for f in os.listdir(DIR_CONV) if f.endswith(".docx") and not f.startswith("~$")]
    print(f"🔍 Auditing {len(files)} files from converted folder...")

    missing = []
    found_count = 0
    all_notion_names = set()
    
    # query_database in notion_api.py handles pagination internally
    res = notion_client.query_database(notion_db_id)
    for page in res.get("results", []):
        title_prop = page["properties"].get("이름", {}).get("title", [])
        if title_prop:
            all_notion_names.add(title_prop[0]["text"]["content"])
    
    print(f"  Loaded {len(all_notion_names)} names from Notion.")

    for f in files:
        if f in all_notion_names:
            found_count += 1
        else:
            missing.append(f)

    print(f"\n✅ Found in Notion: {found_count} / {len(files)}")
    if missing:
        print(f"❌ Missing in Notion ({len(missing)}):")
        for m in missing[:20]: # Show first 20
            print(f"  - {m}")
        if len(missing) > 20:
            print(f"  ... and {len(missing)-20} more.")
    else:
        print("🎉 All converted files are successfully synced to Notion!")

if __name__ == "__main__":
    audit_conv()
