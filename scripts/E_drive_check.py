import json
import time

def check_drive_urls():
    cache = None
    for _ in range(5):
        try:
            with open('candidates_cache_jd.json', 'r', encoding='utf-8') as f:
                cache = json.load(f)
            break
        except Exception:
            time.sleep(1)
            
    if not cache:
        print("Could not load cache safely.")
        return
        
    sample_urls = []
    
    for item in cache:
        url = item.get('drive_url') or item.get('source_url') or item.get('file_link') or item.get('file_url')
        if url and 'drive.google' in url.lower():
            sample_urls.append(url)
            if len(sample_urls) >= 3:
                break
                
    if sample_urls:
        print("Found Google Drive URLs in JSON cache!")
        for u in sample_urls: print(u)
    else:
        print("No Google Drive URLs found in JSON cache.")
        
    # Also check Notion URL
    n_sample = []
    for item in cache:
        if item.get('notion_url'):
            n_sample.append(item['notion_url'])
            if len(n_sample) >= 3:
                break
    print("\nNotion URL 샘플:")
    for n in n_sample: print(n)

if __name__ == "__main__":
    check_drive_urls()
