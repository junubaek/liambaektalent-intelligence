
import os
import json
import sys

PROJECT_ROOT = r"C:\Users\cazam\Downloads\이력서자동분석검색시스템"
sys.path.append(PROJECT_ROOT)

from connectors.gdrive_api import GDriveConnector
from connectors.gemini_api import GeminiClient
from resume_parser import ResumeParser
from connectors.notion_api import NotionClient
from connectors.openai_api import OpenAIClient
from connectors.pinecone_api import PineconeClient

def test_single():
    with open("secrets.json", "r") as f:
        secrets = json.load(f)
    
    # 1. Test GDrive
    print("Testing GDrive...")
    try:
        gdrive = GDriveConnector()
        # Just a test upload of secrets.json to see if SSL hits
        print("  GDrive logic ok.")
    except Exception as e:
        print(f"  ❌ GDrive Error: {e}")

    # 2. Test Gemini
    print("Testing Gemini...")
    try:
        gemini = GeminiClient(secrets["GEMINI_API_KEY"])
        # Simple prompt
        resp = gemini.get_chat_completion_json("return {'hello': 'world'}", model="gemini-1.5-flash")
        print(f"  Gemini Response: {resp}")
    except Exception as e:
        print(f"  ❌ Gemini Error: {e}")

    # 3. Test Notion
    print("Testing Notion...")
    try:
        notion = NotionClient(secrets["NOTION_API_KEY"])
        res = notion.query_database(secrets["NOTION_DATABASE_ID"], limit=1)
        print(f"  Notion OK. Found {len(res.get('results', []))} items.")
    except Exception as e:
        print(f"  ❌ Notion Error: {e}")

    # 4. Test Pinecone
    print("Testing Pinecone...")
    try:
        pc_host = secrets.get("PINECONE_HOST", "").rstrip("/")
        if pc_host and not pc_host.startswith("https://"): pc_host = f"https://{pc_host}"
        pinecone = PineconeClient(secrets["PINECONE_API_KEY"], pc_host)
        res = pinecone.query([0.0]*1536, top_k=1)
        print(f"  Pinecone OK. Matches: {len(res.get('matches', []))}")
    except Exception as e:
        print(f"  ❌ Pinecone Error: {e}")

if __name__ == "__main__":
    test_single()
