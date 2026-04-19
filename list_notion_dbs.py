
import json
import urllib.request
import os

def list_databases():
    secrets_path = r"C:\Users\cazam\Downloads\이력서자동분석검색시스템\secrets.json"
    with open(secrets_path, "r") as f:
        secrets = json.load(f)
    
    api_key = secrets["NOTION_API_KEY"]
    
    url = "https://api.notion.com/v1/search"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Notion-Version": "2022-06-28",
        "Content-Type": "application/json"
    }
    
    payload = {
        "filter": {
            "value": "database",
            "property": "object"
        }
    }
    
    data = json.dumps(payload).encode('utf-8')
    req = urllib.request.Request(url, data=data, headers=headers)
    
    try:
        with urllib.request.urlopen(req) as response:
            result = json.load(response)
            dbs = result.get("results", [])
            if not dbs:
                print("NO_DATABASES_FOUND")
            for db in dbs:
                title = "Untitled"
                if db.get("title"):
                    title = db["title"][0]["plain_text"]
                print(f"DATABASE_FOUND: {title} | ID: {db['id']}")
    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    list_databases()
