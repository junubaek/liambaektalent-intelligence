import json
import requests

def list_props():
    with open('secrets.json', 'r') as f:
        secrets = json.load(f)
    
    NOTION_API_KEY = secrets['NOTION_API_KEY']
    DATABASE_ID = secrets['NOTION_DATABASE_ID']
    
    headers = {
        "Authorization": f"Bearer {NOTION_API_KEY}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28"
    }
    
    url = f"https://api.notion.com/v1/databases/{DATABASE_ID}"
    
    response = requests.get(url, headers=headers)
    props = response.json().get('properties', {})
    for p in props:
        print(f"Property Name: {p} (Type: {props[p]['type']})")

if __name__ == "__main__":
    list_props()
