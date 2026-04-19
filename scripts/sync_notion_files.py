import urllib.request
import json
import os
import time

def sync_notion_files():
    if not os.path.exists('secrets.json'):
        return
        
    with open('secrets.json', 'r', encoding='utf-8') as f:
        secrets = json.load(f)
        
    db_id = secrets.get('NOTION_DATABASE_ID')
    token = secrets.get('NOTION_API_KEY')
    
    url = f"https://api.notion.com/v1/databases/{db_id}/query"
    headers = {
        "Authorization": f"Bearer {token}",
        "Notion-Version": "2022-06-28",
        "Content-Type": "application/json"
    }

    has_more = True
    next_cursor = None
    notion_map = {}
    
    print("Starting Notion Sync for Filenames and Drive Links...")
    
    while has_more:
        try:
            payload = {"page_size": 100}
            if next_cursor:
                payload["start_cursor"] = next_cursor
                
            req = urllib.request.Request(url, data=json.dumps(payload).encode('utf-8'), headers=headers, method='POST')
            res = urllib.request.urlopen(req)
            data = json.loads(res.read())
            
            for page in data.get('results', []):
                pid = page['id']
                props = page.get('properties', {})
                
                # Fetch Drive link
                url_prop = props.get('구글드라이브 링크', {})
                link = url_prop.get('url', '') if url_prop else ''
                
                # Fetch Filename
                file_prop = props.get('파일명', {})
                filename = ""
                if file_prop and file_prop.get('rich_text'):
                    for t in file_prop['rich_text']:
                        filename += t.get('plain_text', '')
                
                notion_map[pid] = {'drive_url': link, 'filename': filename}
                notion_map[pid.replace('-', '')] = {'drive_url': link, 'filename': filename}
                    
            has_more = data.get('has_more', False)
            next_cursor = data.get('next_cursor')
            time.sleep(0.3)
            
        except Exception as e:
            print(f"Error: {e}")
            break

    with open('notion_file_map.json', 'w', encoding='utf-8') as f:
        json.dump(notion_map, f, ensure_ascii=False, indent=2)
        
    print(f"Saved {len(notion_map)} detailed entries.")

if __name__ == "__main__":
    sync_notion_files()
