import json
import requests
import time
import os

CACHE_FILE = "candidates_cache_jd.json"
SECRETS_FILE = "secrets.json"

def patch_notion():
    if not os.path.exists(SECRETS_FILE):
        print("secrets.json not found")
        return
        
    with open(SECRETS_FILE, "r") as f:
        secrets = json.load(f)
        token = secrets.get("NOTION_API_KEY")
        
    if not token:
        print("Notion token missing")
        return

    with open(CACHE_FILE, "r", encoding="utf-8") as f:
        candidates = json.load(f)
        
    headers = {
        "Authorization": f"Bearer {token}",
        "Notion-Version": "2022-06-28",
        "Content-Type": "application/json"
    }
    
    total = len(candidates)
    success = 0
    has_error = False
    
    print(f"Starting to patch {total} candidates in Notion...")
    
    for idx, c in enumerate(candidates, start=1):
        page_id = c.get("id")
        if not page_id:
            continue
            
        props_to_update = {}
        
        name_kr = c.get("name_kr", "")
        # Always update if we have it, even if empty string to clear out garbage
        props_to_update["Name"] = {
            "rich_text": [
                {
                    "text": {
                        "content": name_kr
                    }
                }
            ]
        }
            
        email = c.get("email", "")
        if email:
            props_to_update["이메일"] = {
                "email": email
            }
            
        phone = c.get("phone", "")
        if phone:
            props_to_update["전화번호"] = {
                "phone_number": phone
            }
            
        url = f"https://api.notion.com/v1/pages/{page_id}"
        payload = {"properties": props_to_update}
        
        # Adding a simple retry loop for 429s or transient network issues
        for attempt in range(3):
            try:
                resp = requests.patch(url, headers=headers, json=payload)
                if resp.status_code == 200:
                    success += 1
                    break
                elif resp.status_code == 429:
                    print(f"Rate limited on {name_kr}. Sleeping 2 seconds...")
                    time.sleep(2.0)
                else:
                    if idx < 5:  # Only print first few errors extensively to avoid spam
                        print(f"[{idx}/{total}] Failed to patch {name_kr}. Status: {resp.status_code}. Msg: {resp.text}")
                    has_error = True
                    break
            except Exception as e:
                print(f"Error on {name_kr}: {e}")
                time.sleep(2.0)
            
        if idx % 100 == 0:
            print(f"Progress: {idx}/{total} (Success: {success})")
            
        time.sleep(0.35) # Max ~3 req/s
        
    print(f"Completed! Successfully updated {success} / {total} records.")

if __name__ == "__main__":
    patch_notion()
