
import json
import os
import sys

BASE_PATH = r"C:\Users\cazam\Downloads\이력서자동분석검색시스템"
sys.path.insert(0, BASE_PATH)

from connectors.notion_api import NotionClient

def check_schema():
    secrets_path = os.path.join(BASE_PATH, "secrets.json")
    with open(secrets_path, "r", encoding="utf-8") as f:
        secrets = json.load(f)
    
    client = NotionClient(secrets["NOTION_API_KEY"])
    db_id = secrets["NOTION_DATABASE_ID"]
    
    import urllib.request
    url = f"https://api.notion.com/v1/databases/{db_id}"
    req = urllib.request.Request(url, method="GET")
    req.add_header("Authorization", f"Bearer {secrets['NOTION_API_KEY']}")
    req.add_header("Notion-Version", "2022-06-28")
    req.add_header("Content-Type", "application/json")
    
    with urllib.request.urlopen(req) as response:
        db_data = json.loads(response.read().decode())
        main_sector_options = db_data['properties']['Main Sectors']['multi_select']['options']
        print("EXISTING NOTION OPTIONS:")
        for opt in main_sector_options:
            print(f" - '{opt['name']}'")

if __name__ == "__main__":
    check_schema()
