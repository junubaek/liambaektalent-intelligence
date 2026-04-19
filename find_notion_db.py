
import json
import urllib.request
import os

def find_db_id():
    secrets_path = r"C:\Users\cazam\Downloads\이력서자동분석검색시스템\secrets.json"
    with open(secrets_path, "r") as f:
        secrets = json.load(f)
    
    api_key = secrets["NOTION_API_KEY"]
    page_id = secrets["NOTION_DATABASE_ID"].replace("-", "")
    
    url = f"https://api.notion.com/v1/blocks/{page_id}/children"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Notion-Version": "2022-06-28"
    }
    
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req) as response:
            data = json.load(response)
            for block in data.get("results", []):
                if block["type"] == "child_database":
                    print(f"FOUND_DB_ID: {block['id']}")
                    print(f"DB_TITLE: {block['child_database']['title']}")
                elif block["type"] == "link_to_page" and "database_id" in block["link_to_page"]:
                    print(f"FOUND_LINKED_DB_ID: {block['link_to_page']['database_id']}")
    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    find_db_id()
