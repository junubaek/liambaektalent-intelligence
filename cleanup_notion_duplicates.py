
import json
import os
import sys
import time

# Define base project path
PROJECT_ROOT = r"C:\Users\cazam\Downloads\이력서자동분석검색시스템"
sys.path.append(PROJECT_ROOT)

from connectors.notion_api import NotionClient

def cleanup_duplicates():
    secrets_path = os.path.join(PROJECT_ROOT, "secrets.json")
    with open(secrets_path, "r") as f:
        secrets = json.load(f)
    
    notion = NotionClient(secrets["NOTION_API_KEY"])
    db_id = secrets.get("NOTION_DATABASE_ID", "31f22567-1b6f-8190-b3a8-dc4f8422f01b")
    
    print(f"🚀 [CLEANUP] Starting deduplication for DB: {db_id}")
    
    # 1. Fetch all pages
    res = notion.query_database(db_id)
    all_pages = res.get('results', [])
    print(f"💡 Found {len(all_pages)} total pages.")
    
    # 2. Group by Name
    name_map = {} # name -> [list of page_ids]
    
    for page in all_pages:
        try:
            props = page.get('properties', {})
            title_list = props.get('이름', {}).get('title', [])
            name = "".join([t.get('plain_text', '') for t in title_list]).strip()
            if not name: continue
            
            import re
            clean_name = re.sub(r'\.(doc|docx|pdf)$', '', name, flags=re.IGNORECASE)
            
            if clean_name not in name_map:
                name_map[clean_name] = []
            
            # Store tuple of (last_edited_time, page_id)
            name_map[clean_name].append((page.get('last_edited_time'), page.get('id')))
        except Exception as e:
            print(f"Error parsing page {page.get('id')}: {e}")
            
    # 3. Archive Duplicates
    archive_count = 0
    for name, occurrences in name_map.items():
        if len(occurrences) > 1:
            # Sort by last_edited_time descending
            occurrences.sort(key=lambda x: x[0], reverse=True)
            # Keep the newest one, archive the rest
            to_archive = occurrences[1:]
            print(f"⚠️ Found {len(occurrences)} entries for '{name}'. Archiving {len(to_archive)}...")
            for _, pid in to_archive:
                notion.archive_page(pid)
                archive_count += 1
                time.sleep(0.1) # Avoid rate limit
                
    print(f"\n✨ Cleanup Complete! Archived {archive_count} duplicates.")

if __name__ == "__main__":
    cleanup_duplicates()
