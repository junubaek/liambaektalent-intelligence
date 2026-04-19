import os
import json
import sys

PROJECT_ROOT = r"C:\Users\cazam\Downloads\이력서자동분석검색시스템"
sys.path.append(PROJECT_ROOT)

from connectors.notion_api import HeadhunterDB

def count_missing_patterns():
    secrets_path = os.path.join(PROJECT_ROOT, "secrets.json")
    with open(secrets_path, "r", encoding="utf-8") as f:
        secrets = json.load(f)
        
    db = HeadhunterDB(secrets_path)
    client = db.client
    db_id = secrets.get("NOTION_DATABASE_ID")

    filter_empty = {
        "property": "Functional Patterns",
        "multi_select": {
            "is_empty": True
        }
    }
    
    # Query Database and keep paginating until we get the total count
    all_results = client.query_database(db_id, filter_criteria=filter_empty)
    count = len(all_results.get('results', []))
    print(f"Total candidates missing Functional Patterns: {count}")

if __name__ == "__main__":
    count_missing_patterns()
