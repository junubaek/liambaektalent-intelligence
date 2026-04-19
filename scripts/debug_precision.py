
import os
import sys
import json
import time

# Project setup
PROJECT_ROOT = r"C:\Users\cazam\Downloads\이력서자동분석검색시스템"
sys.path.append(PROJECT_ROOT)

from resume_parser import ResumeParser
from connectors.gemini_api import GeminiClient
from connectors.notion_api import NotionClient
from scripts.backfill_blanks import backfill_single, get_file_map, get_config

def debug_precision():
    secrets = get_config()
    notion = NotionClient(secrets["NOTION_API_KEY"])
    db_id = secrets["NOTION_DATABASE_ID"]
    
    file_map = get_file_map()
    parser = ResumeParser(GeminiClient(secrets["GEMINI_API_KEY"]))
    
    names = ['황영준', '홍창윤', '홍종표', '홍석범', '한계명', '한상덕', '최현철', '최진호', '한정수', '한영빈']
    print(f"🔍 Debugging precision for: {names}")
    
    for name in names:
        print(f"\n--- Searching for {name} ---")
        filter_criteria = {
            "property": "이름",
            "title": {"contains": name}
        }
        res = notion.query_database(db_id, filter_criteria=filter_criteria)
        items = res.get('results', [])
        
        if not items:
            print(f"  ❌ No Notion record found for {name}")
            continue
            
        for p in items:
            p_name = "".join([t['plain_text'] for t in p['properties']['이름']['title']])
            print(f"  Found record: {p_name}")
            backfill_single(p, file_map, secrets, parser)

if __name__ == "__main__":
    debug_precision()
