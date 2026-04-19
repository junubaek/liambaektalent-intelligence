import urllib.request
import json
import os
import time

def sync_drive_links():
    if not os.path.exists('secrets.json'):
        print("secrets.json not found")
        return
        
    with open('secrets.json', 'r', encoding='utf-8') as f:
        secrets = json.load(f)
        
    db_id = secrets.get('NOTION_DATABASE_ID')
    token = secrets.get('NOTION_API_KEY')
    
    if not db_id or not token:
        print("Notion credentials missing")
        return

    url = f"https://api.notion.com/v1/databases/{db_id}/query"
    headers = {
        "Authorization": f"Bearer {token}",
        "Notion-Version": "2022-06-28",
        "Content-Type": "application/json"
    }

    has_more = True
    next_cursor = None
    
    links_map = {}
    
    print("Starting Notion Sync for Google Drive Links...")
    
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
                url_prop = props.get('구글드라이브 링크', {})
                
                link = ""
                if url_prop and url_prop.get('url'):
                    link = url_prop.get('url')
                    
                if link:
                    links_map[pid] = link
                    # Notion UUIDs also come with hyphens. 
                    # Store hyphen-less version as well for robustness.
                    links_map[pid.replace('-', '')] = link
                    
            has_more = data.get('has_more', False)
            next_cursor = data.get('next_cursor')
            print(f"Fetched batch. Current links collected: {len(links_map)}")
            time.sleep(0.3)
            
        except Exception as e:
            print(f"Error fetching batch: {e}")
            break

    output_file = 'drive_links_map.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(links_map, f, ensure_ascii=False, indent=2)
        
    print(f"Done! Saved {len(links_map)} links to {output_file}")

if __name__ == "__main__":
    sync_drive_links()
