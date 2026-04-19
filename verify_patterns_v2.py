import os
from dotenv import load_dotenv
from connectors.notion_api import NotionAPI

load_dotenv()
notion = NotionAPI()
db_id = os.getenv('NOTION_DATABASE_ID')

try:
    db_info = notion.client.databases.retrieve(database_id=db_id)
    options = db_info.get('properties', {}).get('Functional Patterns', {}).get('multi_select', {}).get('options', [])
    print(f'Total unique patterns in Notion database schema for Functional Patterns: {len(options)}')
except Exception as e:
    print(f"Error accessing database: {e}")
