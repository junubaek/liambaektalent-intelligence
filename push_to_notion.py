import json
import os
import requests

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
SECRETS_FILE = os.path.join(ROOT_DIR, "secrets.json")
CACHE_FILE = os.path.join(ROOT_DIR, "candidates_cache_jd.json")

def load_secrets():
    with open(SECRETS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def push_to_notion():
    print("🚀 Starting One-Way Push to Notion...")
    secrets = load_secrets()
    NOTION_API_KEY = secrets.get("NOTION_API_KEY", "").strip()
    
    if not NOTION_API_KEY:
        print("❌ Please provide NOTION_API_KEY in secrets.json")
        return
        
    headers = {
        "Authorization": f"Bearer {NOTION_API_KEY}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28"
    }

    if not os.path.exists(CACHE_FILE):
        print(f"❌ Cache file {CACHE_FILE} not found!")
        return

    with open(CACHE_FILE, "r", encoding="utf-8") as f:
        candidates = json.load(f)

    success_count = 0
    fail_count = 0

    print(f"📦 Total candidates to push: {len(candidates)}")
    for i, cand in enumerate(candidates):
        page_id = cand.get("id")
        if not page_id: continue
        
        # We only push what user requested:
        # name_kr, phone, email, profile_summary, sector, current_company
        properties_payload = {}
        
        if cand.get("name_kr"):
            properties_payload["name_kr"] = {"rich_text": [{"text": {"content": cand["name_kr"]}}]}
        if cand.get("phone"):
            properties_payload["phone"] = {"phone_number": cand["phone"]}
        if cand.get("email"):
            properties_payload["email"] = {"email": cand["email"]}
        if cand.get("profile_summary"):
            properties_payload["profile_summary"] = {"rich_text": [{"text": {"content": cand["profile_summary"]}}]}
        if cand.get("sector"):
            properties_payload["Main Sectors"] = {"select": {"name": cand["sector"]}}
        if cand.get("current_company"):
            properties_payload["현직장"] = {"rich_text": [{"text": {"content": cand["current_company"]}}]}

        if not properties_payload:
            continue

        try:
            url = f"https://api.notion.com/v1/pages/{page_id}"
            res = requests.patch(url, headers=headers, json={"properties": properties_payload})
            
            if res.status_code == 200:
                success_count += 1
            else:
                print(f"❌ Failed to push for {cand.get('name')}: {res.text}")
                fail_count += 1
                
        except Exception as e:
            print(f"❌ Error pushing page {page_id}: {e}")
            fail_count += 1

        if (i+1) % 50 == 0:
            print(f"✅ Sync Progress: {i+1}/{len(candidates)}...")

    print(f"\n✨ Notion Push Complete! Success: {success_count}, Failed: {fail_count}")

if __name__ == "__main__":
    push_to_notion()
