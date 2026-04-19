
import json
import os
import sys

BASE_PATH = r"C:\Users\cazam\Downloads\이력서자동분석검색시스템"
sys.path.insert(0, BASE_PATH)

from connectors.notion_api import NotionClient

def inspect_blanks():
    secrets_path = os.path.join(BASE_PATH, "secrets.json")
    with open(secrets_path, "r", encoding="utf-8") as f:
        secrets = json.load(f)
    
    client = NotionClient(secrets["NOTION_API_KEY"])
    db_id = secrets["NOTION_DATABASE_ID"]
    
    # Query for first 20 blank ones
    filter_blanks = {
        "property": "Main Sectors",
        "multi_select": {"is_empty": True}
    }
    res = client.query_database(db_id, filter_criteria=filter_blanks, limit=20)
    pages = res.get('results', [])
    
    print(f"Found {len(pages)} blank records.")
    for p in pages:
        name = p['properties']['이름']['title'][0]['plain_text']
        print(f" - {name} (ID: {p['id']})")
        # Let's check Sub Sectors too
        sub = p['properties']['Sub Sectors']['multi_select']
        print(f"   Sub Sectors: {sub}")

if __name__ == "__main__":
    inspect_blanks()
