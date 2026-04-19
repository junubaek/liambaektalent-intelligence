import json
import requests

# Load Secrets
with open("c:/Users/cazam/Downloads/이력서자동분석검색시스템/secrets.json", "r") as f:
    secrets = json.load(f)

NOTION_TOKEN = secrets["NOTION_API_KEY"]
PARENT_PAGE_ID = "2ce22567-1b6f-8084-8f00-f20994eae35e" 
HEADERS = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28"
}

def create_discovery_hub():
    print("🚀 Initializing Market Trend Discovery Hub (v6.3.1)...")
    
    db_payload = {
        "parent": {"type": "page_id", "page_id": PARENT_PAGE_ID},
        "title": [{"type": "text", "text": {"content": "📈 Market Trend Discovery Queue (v6.3.1)"}}],
        "properties": {
            "임시 패턴명": {"title": {}},
            "발견 출처": {"select": {"options": [
                {"name": "JD (수요)", "color": "blue"},
                {"name": "Resume (공급)", "color": "green"},
                {"name": "Both", "color": "purple"}
            ]}},
            "발견 횟수": {"number": {}},
            "섹터": {"select": {}},
            "희소성 예측": {"select": {"options": [
                {"name": "Extremely High", "color": "red"},
                {"name": "High", "color": "orange"},
                {"name": "Medium", "color": "yellow"},
                {"name": "Low", "color": "gray"}
            ]}},
            "원문 데이터": {"rich_text": {}},
            "상태": {"select": {"options": [
                {"name": "New", "color": "blue"},
                {"name": "Review", "color": "yellow"},
                {"name": "Promoted", "color": "green"},
                {"name": "Merged", "color": "gray"},
                {"name": "Rejected", "color": "red"}
            ]}}
        }
    }
    
    response = requests.post("https://api.notion.com/v1/databases", headers=HEADERS, json=db_payload)
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Created Discovery Hub: {data['url']}")
        print(f"   Database ID: {data['id']}")
    else:
        print(f"❌ Failed to create Discovery Hub: {response.text}")

if __name__ == "__main__":
    create_discovery_hub()
