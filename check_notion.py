import urllib.request
import json
import os

def check_db():
    if not os.path.exists('secrets.json'): return
    with open('secrets.json', 'r', encoding='utf-8') as f:
        d = json.load(f)
    
    db_id = d.get('NOTION_DATABASE_ID')
    token = d.get('NOTION_API_KEY')
    
    req = urllib.request.Request(
        f"https://api.notion.com/v1/databases/{db_id}",
        headers={'Authorization': f'Bearer {token}', 'Notion-Version': '2022-06-28'}
    )
    
    try:
        res = urllib.request.urlopen(req)
        data = json.loads(res.read())
        props = data.get('properties', {})
        print(json.dumps(props, indent=2, ensure_ascii=False))
    except Exception as e:
        print(e)
        
if __name__ == "__main__":
    check_db()
