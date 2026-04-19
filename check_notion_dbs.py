
import json
import urllib.request
import os

def check_dbs():
    secrets_path = r"C:\Users\cazam\Downloads\이력서자동분석검색시스템\secrets.json"
    with open(secrets_path, "r") as f:
        secrets = json.load(f)
    
    api_key = secrets["NOTION_API_KEY"]
    
    # List of candidate IDs from previous search
    candidates = [
        ("Search", "1bf22567-1b6f-80f6-be45-d7fe5db11844"),
        ("Resume DB (Auto-Created)", "30a22567-1b6f-81c3-9d33-d480330553c0"),
        ("Untitled", "23022567-1b6f-808e-9ec9-dc981fd68b01"),
        ("디벨롭중", "643cedc2-a80b-4a62-ad8b-59ff71016523")
    ]
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Notion-Version": "2022-06-28"
    }
    
    for name, db_id in candidates:
        print(f"\nChecking DB: {name} ({db_id})")
        url = f"https://api.notion.com/v1/databases/{db_id}"
        req = urllib.request.Request(url, headers=headers)
        try:
            with urllib.request.urlopen(req) as response:
                result = json.load(response)
                props = result.get("properties", {}).keys()
                print(f"PROPERTIES: {list(props)}")
                if "Primary Sector" in props or "Experience Patterns" in props:
                    print(">>> POTENTIAL MATCH FOUND!")
        except Exception as e:
            print(f"ERROR checking {db_id}: {e}")

if __name__ == "__main__":
    check_dbs()
