import os
import json
import requests

# Configuration
with open("secrets.json", "r") as f:
    secrets = json.load(f)

NOTION_TOKEN = secrets["NOTION_API_KEY"]
NOTION_DB_ID = secrets["NOTION_DATABASE_ID"]

headers = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28"
}

TARGET_NAMES = ["이정한", "김정근", "심초아", "이종민", "장봉원", "전예찬", "전형준", "정예린", "정현구", "정현우", "정호진", "최재언", "황의영", "박주령", "강병수"]

def check_targets():
    print("🔍 Checking status of 15 target candidates...")
    url = f"https://api.notion.com/v1/databases/{NOTION_DB_ID}/query"
    has_more = True
    next_cursor = None
    results = []
    
    while has_more:
        payload = {"page_size": 100}
        if next_cursor: payload["start_cursor"] = next_cursor
        resp = requests.post(url, headers=headers, json=payload).json()
        for p in resp.get('results', []):
            if p.get('archived'): continue
            props = p['properties']
            name_list = props.get('이름', {}).get('title', [])
            name = name_list[0]['plain_text'] if name_list else "Unknown"
            
            if any(tn in name for tn in TARGET_NAMES):
                patterns = len(props.get('Experience Patterns', {}).get('multi_select', []))
                summary = len(props.get('경력 Summary', {}).get('rich_text', []))
                sector = len(props.get('Primary Sector', {}).get('multi_select', []))
                link = props.get('구글드라이브 링크', {}).get('url')
                
                results.append({
                    "name": name,
                    "patterns": patterns,
                    "summary": summary,
                    "sector": sector,
                    "link": "OK" if link else "MISSING"
                })
        has_more = resp.get('has_more', False)
        next_cursor = resp.get('next_cursor')

    print("\n| Name | Patterns | Summary | Sector | Link |")
    print("| :--- | :--- | :--- | :--- | :--- |")
    for r in sorted(results, key=lambda x: x['name']):
        print(f"| {r['name']} | {r['patterns']} | {r['summary']} | {r['sector']} | {r['link']} |")

if __name__ == "__main__":
    check_targets()
