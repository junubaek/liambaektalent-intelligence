import os
import json
import urllib.request
import urllib.error

def fetch_schema():
    with open("secrets.json", "r", encoding="utf-8") as f:
        secrets = json.load(f)
        
    token = secrets["NOTION_API_KEY"]
    db_id = secrets["NOTION_DATABASE_ID"]
    
    url = f"https://api.notion.com/v1/databases/{db_id}"
    req = urllib.request.Request(url, headers={"Authorization": f"Bearer {token}", "Notion-Version": "2022-06-28"})
    
    try:
        with urllib.request.urlopen(req) as response:
            res = json.loads(response.read().decode('utf-8'))
            props = res.get("properties", {})
            
            main_sectors = []
            if "Main Sector" in props and "select" in props["Main Sector"]:
                main_sectors = [opt["name"] for opt in props["Main Sector"]["select"].get("options", [])]
                
            sub_sectors = []
            if "Sub Sector" in props and "select" in props["Sub Sector"]:
                sub_sectors = [opt["name"] for opt in props["Sub Sector"]["select"].get("options", [])]
                
            print(f"MAIN_SECTORS = {main_sectors}")
            print(f"SUB_SECTORS = {sub_sectors}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    fetch_schema()
