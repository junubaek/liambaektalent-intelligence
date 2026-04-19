
import json
import os
import sys

# Define base path to ensure correct loading of secrets
BASE_PATH = r"C:\Users\cazam\Downloads\이력서자동분석검색시스템"
sys.path.insert(0, BASE_PATH)

from connectors.notion_api import NotionClient

def get_count():
    secrets_path = os.path.join(BASE_PATH, "secrets.json")
    with open(secrets_path, "r", encoding="utf-8") as f:
        secrets = json.load(f)
    
    notion_db_id = secrets["NOTION_DATABASE_ID"]
    client = NotionClient(secrets["NOTION_API_KEY"])
    
    print(f"Checking Notion DB: {notion_db_id}...")
    # query_database handles pagination and returns all results
    res = client.query_database(notion_db_id)
    print(f"COUNT: {len(res.get('results', []))}")

if __name__ == "__main__":
    get_count()
