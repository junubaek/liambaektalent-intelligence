
import json
import sys
from connectors.notion_api import NotionClient

def inspect_specific_db(db_id):
    with open("secrets.json", "r") as f:
        secrets = json.load(f)
    client = NotionClient(secrets["NOTION_API_KEY"])
    
    db = client._request("GET", f"databases/{db_id}")
    if db:
        title_obj = db.get('title', [])
        title = title_obj[0].get('plain_text', 'Unknown') if title_obj else 'No Title'
        print(f"\n--- Database: {title} ({db_id}) ---")
        print("Properties:")
        for name, prop in db.get('properties', {}).items():
            print(f" - {name}: {prop['type']}")
    else:
        print(f"Failed to fetch {db_id}")

if __name__ == "__main__":
    ids = [
        "756285ea-c39e-4315-8530-8e4154488d03", # PROGRAM
        "1ef4807f-4b58-4fec-ab66-5c2e593b1ca4"  # PROJECT
    ]
    for d_id in ids:
        inspect_specific_db(d_id)
