import os
import json
import time
import sys
import re
from concurrent.futures import ThreadPoolExecutor
from functools import partial

# Project setup
PROJECT_ROOT = r"C:\Users\cazam\Downloads\이력서자동분석검색시스템"
sys.path.append(PROJECT_ROOT)

from resume_parser import ResumeParser
from connectors.gemini_api import GeminiClient
from connectors.notion_api import NotionClient
from unified_rebuild_and_sync import extract_text, CANONICAL_MAIN_SECTORS, CANONICAL_SUB_SECTORS, DIR_RAW, DIR_CONV, DIR_CONV_V8

def get_config():
    secrets_path = os.path.join(PROJECT_ROOT, "secrets.json")
    with open(secrets_path, "r", encoding="utf-8") as f:
        secrets = json.load(f)
    return secrets

def get_file_map():
    file_map = {}
    # Folders to search for resumes
    dirs = [DIR_RAW, DIR_CONV, DIR_CONV_V8]
    for d in dirs:
        if os.path.exists(d):
            for f in os.listdir(d):
                if f.lower().endswith(('.pdf', '.docx')) and not f.startswith("~$"):
                    # We use the filename (without extension) as the key
                    name_base = os.path.splitext(f)[0]
                    file_map[name_base] = os.path.join(d, f)
    return file_map

def find_best_file(target_name, file_map):
    # 1. Exact match
    if target_name in file_map:
        return file_map[target_name]
    
    # 2. Fuzzy match: target_name is in filename or vice versa
    target_clean = target_name.replace(" ", "").lower()
    for fbase, fpath in file_map.items():
        fbase_clean = fbase.replace(" ", "").lower()
        if target_clean in fbase_clean or fbase_clean in target_clean:
            return fpath
            
    return None

def repair_single(name, file_map, secrets, parser, notion_client, db_id):
    try:
        print(f"[*] Targeting: {name}")
        
        # 1. Find file
        filepath = find_best_file(name, file_map)
        if not filepath:
            print(f"  [Skip] File not found for: {name}")
            return False
            
        # 2. Extract text (Front to Back)
        text = extract_text(filepath)
        if len(text) < 100:
            print(f"  ⚠️ Warning: Very short text ({len(text)} chars) for {name}.")
            
        # 3. Deep Parse using AI
        # We wrap the text with a specific instruction to look at the whole content
        deep_text = f"[INSTRUCTION: ANALYZE THE ENTIRE DOCUMENT BELOW. LOOK AT THE BACK PART FOR SECTOR CLASSIFICATION IF NEEDED]\n\n{text}"
        parsed_data = parser.parse(deep_text)
        
        if not parsed_data:
            print(f"  ❌ AI extraction failed for {name}")
            return False
            
        profile = parsed_data.get("candidate_profile", {})
        patterns = parsed_data.get("patterns", [])
        
        # 4. Map to Canonical Sectors
        main_sectors = []
        for s in profile.get("main_sectors", []):
            s_stripped = s.strip()
            if s_stripped in CANONICAL_MAIN_SECTORS:
                main_sectors.append({"name": s_stripped})
                
        sub_sectors = []
        for s in profile.get("sub_sectors", []):
            s_stripped = s.strip()
            if s_stripped in CANONICAL_SUB_SECTORS:
                sub_sectors.append({"name": s_stripped})
                
        # 5. Find the page in Notion
        query_filter = {"property": "이름", "title": {"contains": name}}
        results = notion_client.query_database(db_id, filter_criteria=query_filter).get('results', [])
        
        if not results:
            print(f"  ⚠️ Could not find page in Notion for {name}")
            return False
            
        # Update the first matching page
        page_id = results[0]['id']
        current_props = results[0]['properties']
        
        # Prepare updates (only fill if empty or specifically updating)
        update_props = {}
        
        # Always update sectors for precision
        update_props["Main Sectors"] = {"multi_select": main_sectors}
        update_props["Sub Sectors"] = {"multi_select": sub_sectors}
        
        # Update summary if blank
        if not current_props.get('Experience Summary', {}).get('rich_text'):
            exp_summary = profile.get("experience_summary", "")
            if isinstance(exp_summary, list): exp_summary = "\n".join(exp_summary)
            if exp_summary:
                update_props["Experience Summary"] = {"rich_text": [{"text": {"content": exp_summary[:2000]}}]}
                
        # Update Context Tags if blank
        if not current_props.get('Context Tags', {}).get('rich_text'):
            tags = ", ".join(profile.get("context_tags", []))
            if tags:
                update_props["Context Tags"] = {"rich_text": [{"text": {"content": tags[:2000]}}]}
                
        # Update Functional Patterns if blank
        if not current_props.get('Functional Patterns', {}).get('multi_select'):
            pattern_list = [{"name": p.get("verb_object", "").replace(",", "/").strip()[:100]} for p in patterns if p.get("verb_object", "").strip()]
            if pattern_list:
                update_props["Functional Patterns"] = {"multi_select": pattern_list}

        # Metadata
        update_props["AI Last Optimized"] = {"date": {"start": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}}
        
        notion_client.update_page_properties(page_id, update_props)
        print(f"  ✅ Updated: {name} (Main: {len(main_sectors)}, Sub: {len(sub_sectors)})")
        return True
        
    except Exception as e:
        print(f"  ❌ Error for {name}: {e}")
        return False

def main_repair():
    target_names = [
        "장원", "추지철", "소금지", "서혁", "변정희", "박종순", "두민영", "남상훈", "김진원", "김건우", 
        "강희범", "류길문", "이제호", "홍현종", "진상현", "주현", "이용진", "이동혁", "이정호", "이규원", 
        "유지훈", "양원희", "양동진", "신홍선", "정민치", "노현관", "김현득", "김준호", "김정아", "김민준", 
        "김기찬", "강지선", "임영택", "이진호", "박해진", "유창기", "류제천", "김한울", "김정호"
    ]
    
    secrets = get_config()
    notion_client = NotionClient(secrets["NOTION_API_KEY"])
    db_id = secrets["NOTION_DATABASE_ID"]
    file_map = get_file_map()
    parser = ResumeParser(GeminiClient(secrets["GEMINI_API_KEY"]))
    
    print(f"🚀 Starting Targeted Repair for {len(target_names)} candidates...")
    
    success_count = 0
    # Sequential run for better logging and rate limit safety during repair
    for name in target_names:
        if repair_single(name, file_map, secrets, parser, notion_client, db_id):
            success_count += 1
        time.sleep(1) # Small delay for Notion API
        
    print(f"\n✨ Repair Complete. Success: {success_count}/{len(target_names)}")

if __name__ == "__main__":
    main_repair()
