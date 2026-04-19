
import json
import urllib.request
import os

def create_master_hub():
    secrets_path = r"C:\Users\cazam\Downloads\이력서자동분석검색시스템\secrets.json"
    with open(secrets_path, "r") as f:
        secrets = json.load(f)
    
    api_key = secrets["NOTION_API_KEY"]
    # The parent page ID provided by the user
    parent_page_id = "2ce22567-1b6f-8084-8f00-f20994eae35e"
    
    url = "https://api.notion.com/v1/databases"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Notion-Version": "2022-06-28",
        "Content-Type": "application/json"
    }
    
    payload = {
        "parent": {"type": "page_id", "page_id": parent_page_id},
        "title": [{"type": "text", "text": {"content": "🌌 AI Talent Intelligence v8.0 Master Hub"}}],
        "properties": {
            "이름": {"title": {}},
            "Primary Sector": {
                "select": {
                    "options": [
                        {"name": "SW", "color": "blue"},
                        {"name": "HW", "color": "green"},
                        {"name": "반도체", "color": "orange"},
                        {"name": "AI", "color": "purple"},
                        {"name": "보안", "color": "red"},
                        {"name": "마케팅", "color": "pink"},
                        {"name": "영업", "color": "yellow"},
                        {"name": "디자인", "color": "gray"},
                        {"name": "PRODUCT", "color": "brown"}
                    ]
                }
            },
            "Seniority Bucket": {
                "select": {
                    "options": [
                        {"name": "Junior", "color": "blue"},
                        {"name": "Middle", "color": "orange"},
                        {"name": "Senior", "color": "red"}
                    ]
                }
            },
            "Functional Patterns": {"multi_select": {}},
            "Context Tags": {"multi_select": {}},
            "구글드라이브 링크": {"url": {}}
        }
    }
    
    data = json.dumps(payload).encode('utf-8')
    req = urllib.request.Request(url, data=data, headers=headers)
    
    try:
        with urllib.request.urlopen(req) as response:
            result = json.load(response)
            new_db_id = result.get("id")
            print(f"NEW_DB_CREATED_ID: {new_db_id}")
            return new_db_id
    except Exception as e:
        # If it's a 400 error because the parent is not shared or found
        print(f"ERROR creating database: {e}")
        return None

if __name__ == "__main__":
    create_master_hub()
