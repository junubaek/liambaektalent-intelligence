import json
import sqlite3
import time
import urllib.request
import concurrent.futures

def extract_drive_url(item, headers):
    notion_url = item.get('notion_url')
    if not notion_url:
        return item['id'], None
    page_id = notion_url.split('/')[-1]
    url = f"https://api.notion.com/v1/pages/{page_id}"
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode('utf-8'))
            props = data.get('properties', {})
            url_props = [v['url'] for k, v in props.items() if v['type'] == 'url' and v['url'] and 'drive.google' in v['url']]
            return item['id'], url_props[0] if url_props else None
    except Exception as e:
        return item['id'], None

def main():
    print("Starting Optimized Notion to Google Drive Tracking...")
    with open("secrets.json", "r") as f:
        secrets = json.load(f)
        
    headers = {
        "Authorization": f"Bearer {secrets['NOTION_API_KEY']}",
        "Notion-Version": "2022-06-28"
    }
    
    conn = sqlite3.connect("candidates.db", timeout=30)
    c = conn.cursor()
    
    cache_path = 'candidates_cache_jd.json'
    with open(cache_path, 'r', encoding='utf-8') as f:
        cache = json.load(f)
        
    # Find targets
    to_process = [item for item in cache if item.get('notion_url') and not item.get('google_drive_url')]
    total = len(to_process)
    print(f"Found {total} candidates needing google_drive_url.")
    
    success = 0
    fail = 0
    
    results = []
    
    # Process with 4 workers to stay near 3req/s with latency overhead
    start_time = time.time()
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        futures = {executor.submit(extract_drive_url, item, headers): item for item in to_process}
        
        for i, future in enumerate(concurrent.futures.as_completed(futures)):
            cid, drive_url = future.result()
            if drive_url:
                results.append((drive_url, cid))
                success += 1
            else:
                fail += 1
                
            if (i+1) % 50 == 0:
                print(f"Processed: {i+1}/{total} (Success: {success}, Fail: {fail})")
                
            time.sleep(0.1) # Soften the blow to Notion API
            
    # Batch update SQLite to avoid locks
    if results:
        c.executemany("UPDATE candidates SET google_drive_url=? WHERE id=?", results)
        conn.commit()
        
        # Update JSON cache inline
        cache_map = {item['id']: item for item in cache}
        for drive_url, cid in results:
            if cid in cache_map:
                cache_map[cid]['google_drive_url'] = drive_url
                
        with open(cache_path, 'w', encoding='utf-8') as f:
            json.dump(cache, f, ensure_ascii=False, indent=2)
            
    conn.close()
    elapsed = time.time() - start_time
    print(f"Batch completed in {elapsed:.1f}s! Successfully found {success} URLs.")

if __name__ == "__main__":
    main()
