import os
import json
import requests
from dotenv import load_dotenv

load_dotenv()

notion_token = os.getenv('NOTION_API_KEY')
db_id = os.getenv('NOTION_DATABASE_ID')

headers = {
    'Authorization': f'Bearer {notion_token}',
    'Notion-Version': '2022-06-28',
    'Content-Type': 'application/json'
}

response = requests.get(f'https://api.notion.com/v1/databases/{db_id}', headers=headers)

if response.status_code == 200:
    data = response.json()
    options = data.get('properties', {}).get('Functional Patterns', {}).get('multi_select', {}).get('options', [])
    print(f'Total unique patterns in Notion database schema for Functional Patterns: {len(options)}')
else:
    print(f"Error fetching database: {response.status_code} - {response.text}")
