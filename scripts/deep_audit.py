
import json
import os
import sys

BASE_PATH = r"C:\Users\cazam\Downloads\이력서자동분석검색시스템"
sys.path.insert(0, BASE_PATH)

from connectors.notion_api import NotionClient

def deep_audit():
    secrets_path = os.path.join(BASE_PATH, "secrets.json")
    with open(secrets_path, "r", encoding="utf-8") as f:
        secrets = json.load(f)
    
    client = NotionClient(secrets["NOTION_API_KEY"])
    db_id = secrets["NOTION_DATABASE_ID"]
    
    # Query all records (paginated)
    all_pages = client.query_database(db_id)
    pages = all_pages.get('results', [])
    
    total = len(pages)
    blank_main = 0
    blank_sub = 0
    
    for p in pages:
        props = p['properties']
        if not props['Main Sectors']['multi_select']:
            blank_main += 1
        if not props['Sub Sectors']['multi_select']:
            blank_sub += 1
            
    print(f"DEEP AUDIT RESULTS (Top {total} records):")
    print(f" - Main Sectors Blank: {blank_main}/{total} ({blank_main/total*100:.1f}%)")
    print(f" - Sub Sectors Blank: {blank_sub}/{total} ({blank_sub/total*100:.1f}%)")

if __name__ == "__main__":
    deep_audit()
