
import json
import os
import sys

BASE_PATH = r"C:\Users\cazam\Downloads\이력서자동분석검색시스템"
sys.path.insert(0, BASE_PATH)

from connectors.notion_api import NotionClient

def audit_blanks():
    secrets_path = os.path.join(BASE_PATH, "secrets.json")
    with open(secrets_path, "r", encoding="utf-8") as f:
        secrets = json.load(f)
    
    notion_db_id = secrets["NOTION_DATABASE_ID"]
    client = NotionClient(secrets["NOTION_API_KEY"])
    
    print(f"🔍 Auditing Blanks for DB: {notion_db_id}...")
    res = client.query_database(notion_db_id, limit=100) # Sample 100
    pages = res.get('results', [])
    
    if not pages:
        print("No pages found.")
        return

    # Tracking blanks per property
    stats = {}
    sample_size = len(pages)
    
    for page in pages:
        props = page.get('properties', {})
        for name, prop in props.items():
            ptype = prop['type']
            is_empty = False
            
            if ptype == 'title':
                is_empty = len(prop['title']) == 0
            elif ptype == 'rich_text':
                is_empty = len(prop['rich_text']) == 0
            elif ptype == 'multi_select':
                is_empty = len(prop['multi_select']) == 0
            elif ptype == 'select':
                is_empty = prop['select'] is None
            elif ptype == 'url':
                is_empty = prop['url'] is None
            elif ptype == 'date':
                is_empty = prop['date'] is None
            
            if name not in stats: stats[name] = 0
            if is_empty: stats[name] += 1

    print(f"\nBlank Field Audit (Sample: {sample_size}):")
    for name, count in stats.items():
        percentage = (count / sample_size) * 100
        print(f"  - {name:25}: {count:3} blanks ({percentage:5.1f}%)")

if __name__ == "__main__":
    audit_blanks()
