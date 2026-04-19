import json
import sqlite3
import time
import urllib.request
import traceback

def extract_drive_url(notion_url, headers):
    if not notion_url:
        return None
    page_id = notion_url.split('/')[-1]
    url = f"https://api.notion.com/v1/pages/{page_id}"
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode('utf-8'))
            props = data.get('properties', {})
            url_props = [v['url'] for k, v in props.items() if v['type'] == 'url' and v['url'] and 'drive.google' in v['url']]
            return url_props[0] if url_props else None
    except Exception as e:
        return None

def main():
    print("Starting Notion to Google Drive Reverse-Tracking Batch...")
    with open("secrets.json", "r") as f:
        secrets = json.load(f)
        
    headers = {
        "Authorization": f"Bearer {secrets['NOTION_API_KEY']}",
        "Notion-Version": "2022-06-28"
    }
    
    conn = sqlite3.connect("candidates.db", timeout=20)
    c = conn.cursor()
    
    # Load JSON cache
    cache_path = 'candidates_cache_jd.json'
    try:
        with open(cache_path, 'r', encoding='utf-8') as f:
            cache = json.load(f)
    except Exception:
        print("Failed to load JSON cache.")
        return
        
    # We only process candidates that need updating
    to_process = []
    for item in cache:
        cid = str(item['id'])
        notion_url = item.get('notion_url')
        drive_url = item.get('google_drive_url')
        
        # Only if we have a notion URL and NO google drive URL
        if notion_url and not drive_url:
            to_process.append(item)
            
    total = len(to_process)
    print(f"Found {total} candidates with notion_url but no google_drive_url.")
    
    success = 0
    fail = 0
    save_interval = 50
    
    for i, item in enumerate(to_process):
        cid = item['id']
        notion_url = item['notion_url']
        
        drive_url = extract_drive_url(notion_url, headers)
        
        if drive_url:
            item['google_drive_url'] = drive_url
            c.execute("UPDATE candidates SET google_drive_url=? WHERE id=?", (drive_url, cid))
            success += 1
        else:
            fail += 1
            
        time.sleep(0.4) # Rate limit: 3/sec
        
        if (i+1) % save_interval == 0:
            print(f"Progress: {i+1}/{total} | Extracted: {success} | Failed: {fail}")
            conn.commit()
            with open(cache_path, 'w', encoding='utf-8') as f:
                json.dump(cache, f, ensure_ascii=False, indent=2)
                
    # Final save
    conn.commit()
    with open(cache_path, 'w', encoding='utf-8') as f:
        json.dump(cache, f, ensure_ascii=False, indent=2)
        
    conn.close()
    print(f"Batch completed! Successfully traced {success} Google Drive URLs.")

if __name__ == "__main__":
    main()
