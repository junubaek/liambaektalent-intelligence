
import os
import json
import hashlib
import time
import sys
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
    for d in [DIR_RAW, DIR_CONV, DIR_CONV_V8]:
        if os.path.exists(d):
            for f in os.listdir(d):
                if f.lower().endswith(('.pdf', '.docx')) and not f.startswith("~$"):
                    name_base = os.path.splitext(f)[0]
                    file_map[name_base] = os.path.join(d, f)
    return file_map

def backfill_single(page, file_map, secrets, parser):
    try:
        props = page['properties']
        name = "".join([t['plain_text'] for t in props['이름']['title']])
        page_id = page['id']
        
        if name not in file_map:
            # Try a fuzzy match or check if name is in filename
            found_path = None
            name_clean = name.replace(" ", "").lower()
            for fbase, fpath in file_map.items():
                fbase_clean = fbase.replace(" ", "").lower()
                if name_clean in fbase_clean or fbase_clean in name_clean:
                    found_path = fpath
                    break
            
            if not found_path:
                print(f"  [Skip] File not found for: {name}")
                return False
            final_path = found_path
        else:
            final_path = file_map[name]
            
        print(f"[*] Recovering: {name}")
        text = extract_text(final_path)
        # Fallback: if text is very short, lead with the name to provide context
        if len(text) < 600:
            text = f"Candidate Name/Role Info: {name}\n\nDocument Content:\n{text}"
            
        print(f"    - Text size: {len(text)} chars")
        if len(text) < 100:
            print(f"  ⚠️ Warning: Very short text for {name}. Extraction might have failed.")
        
        parsed_data = parser.parse(text)
        if not parsed_data: 
            print(f"  ❌ AI failed for {name}")
            return False
        
        profile = parsed_data.get("candidate_profile", {})
        patterns = parsed_data.get("patterns", [])
        
        orig_main = profile.get("main_sectors", [])
        orig_sub = profile.get("sub_sectors", [])
        
        canonical_map_main = {s.lower().strip(): s for s in CANONICAL_MAIN_SECTORS}
        # Also map the Korean-only prefix for common sectors
        for s in CANONICAL_MAIN_SECTORS:
            if "(" in s:
                prefix = s.split("(")[0].strip().lower()
                if prefix not in canonical_map_main:
                    canonical_map_main[prefix] = s

        canonical_map_sub = {s.lower().strip(): s for s in CANONICAL_SUB_SECTORS}

        # Strict mapping
        main_sectors = []
        for s in orig_main:
            s_clean = s.strip().lower()
            if s_clean in canonical_map_main:
                main_sectors.append({"name": canonical_map_main[s_clean]})
            else:
                # Try partial match for safety
                found = False
                for k, v in canonical_map_main.items():
                    if s_clean in k or k in s_clean:
                        main_sectors.append({"name": v})
                        found = True
                        break
                if not found:
                    print(f"  ⚠️ Main Sector Mismatch: '{s}' not in CANONICAL list for {name}")

        sub_sectors = []
        for s in orig_sub:
            s_clean = s.strip().lower()
            if s_clean in canonical_map_sub:
                sub_sectors.append({"name": canonical_map_sub[s_clean]})
        
        # Recovery properties
        if not main_sectors and orig_main:
            print(f"  🚨 FAILED to map ANY Main Sectors for {name}. AI said: {orig_main}")
        elif not main_sectors:
            print(f"  ℹ️ No sectors found by AI for {name}")
        
        exp_summary = profile.get("experience_summary", "")
        if isinstance(exp_summary, list): exp_summary = "\n".join(exp_summary)
        
        notion = NotionClient(secrets["NOTION_API_KEY"])
        notion.update_page_properties(page_id, {
            "Main Sectors": {"multi_select": main_sectors},
            "Sub Sectors": {"multi_select": sub_sectors},
            "Context Tags": {"rich_text": [{"text": {"content": ", ".join(profile.get("context_tags", []))[:2000]}}]},
            "Experience Summary": {"rich_text": [{"text": {"content": exp_summary[:2000]}}]},
            "Seniority Bucket": {"select": {"name": (profile.get("seniority_bucket") or "Unknown")}},
            "Functional Patterns": {"multi_select": [{"name": p.get("verb_object", "").strip()[:100]} for p in patterns if p.get("verb_object", "").strip()]},
            "AI Last Optimized": {"date": {"start": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}}
        })
        print(f"  ✅ Updated: {name} (Main: {len(main_sectors)}, Sub: {len(sub_sectors)})")
        return True
    except Exception as e:
        print(f"  ❌ Error for {name}: {e}")
        return False

def main_backfill():
    secrets = get_config()
    notion = NotionClient(secrets["NOTION_API_KEY"])
    db_id = secrets["NOTION_DATABASE_ID"]
    
    file_map = get_file_map()
    parser = ResumeParser(GeminiClient(secrets["GEMINI_API_KEY"]))

    while True:
        print(f"🔍 Batch: Searching for records with ANY intelligence gaps (Sub/Tag/Summary)...")
        # Holistic filter: Main is 기타 OR Sub/Tag/Summary is empty
        filter_completeness = {
            "or": [
                {"property": "Main Sectors", "multi_select": {"contains": "기타"}},
                {"property": "Sub Sectors", "multi_select": {"is_empty": True}},
                {"property": "Context Tags", "rich_text": {"is_empty": True}},
                {"property": "Experience Summary", "rich_text": {"is_empty": True}}
            ]
        }
        
        res = notion.query_database(db_id, filter_criteria=filter_completeness, limit=100)
        target_pages = res.get('results', [])
        
        if not target_pages:
            print("✨ No more target records found. Precision Sync COMPLETE!")
            break
            
        print(f"💡 Found {len(target_pages)} records in this batch.")
        
        max_workers = 5
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            worker_fn = partial(backfill_single, file_map=file_map, secrets=secrets, parser=parser)
            results = list(executor.map(worker_fn, target_pages))
        
        success = sum(1 for r in results if r)
        print(f"✅ Batch Complete. Recovered: {success}/{len(target_pages)}")
        
        # If we couldn't recover any in a batch, something might be stuck. 
        # But we'll keep going for now as there might be many records.
        if success == 0:
            print("⚠️ Warning: Zero records recovered in this batch. Breaking to avoid infinite loop.")
            break

if __name__ == "__main__":
    main_backfill()
