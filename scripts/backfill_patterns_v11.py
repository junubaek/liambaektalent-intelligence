import os
import json
import logging
import sys
import difflib

PROJECT_ROOT = r"C:\Users\cazam\Downloads\이력서자동분석검색시스템"
sys.path.append(PROJECT_ROOT)

from connectors.notion_api import HeadhunterDB
from connectors.gemini_api import GeminiClient
from resume_parser import ResumeParser

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def add_pattern_safe_dynamic(new_pattern: str, existing_patterns: list, max_limit=90) -> str:
    """Safe addition of patterns respecting the specified max limit (90)."""
    if len(existing_patterns) >= max_limit:
        # If over limit, find closest match or fallback to the first one safely
        matches = difflib.get_close_matches(new_pattern, existing_patterns, n=1, cutoff=0.3)
        return matches[0] if matches else (existing_patterns[0] if existing_patterns else new_pattern)
    return new_pattern

def run_pattern_backfill():
    secrets_path = os.path.join(PROJECT_ROOT, "secrets.json")
    with open(secrets_path, "r", encoding="utf-8") as f:
        secrets = json.load(f)
        
    db = HeadhunterDB(secrets_path)
    client = db.client
    db_id = secrets.get("NOTION_DATABASE_ID")
    
    gemini = GeminiClient(secrets["GEMINI_API_KEY"])
    parser = ResumeParser(gemini)

    # 1. Fetch Existing Patterns from Notion
    logger.info("Fetching existing Functional Patterns schema from Notion...")
    existing_patterns = []
    db_info = client._request("GET", f"databases/{db_id}")
    if db_info and "properties" in db_info and "Functional Patterns" in db_info["properties"]:
        options = db_info["properties"]["Functional Patterns"].get("multi_select", {}).get("options", [])
        existing_patterns = [opt["name"] for opt in options]
    
    logger.info(f"Loaded {len(existing_patterns)} existing patterns. Limit set to 90.")

    # 2. Query All Candidates without patterns
    logger.info("Querying candidates missing Functional Patterns...")
    
    # Query logic: Filter where Functional Patterns is empty.
    # Because it is multi_select, we check for emptiness
    filter_empty = {
        "property": "Functional Patterns",
        "multi_select": {
            "is_empty": True
        }
    }
    
    res = client.query_database(db_id, filter_criteria=filter_empty, limit=100)
    pages = res.get('results', [])
    logger.info(f"Found {len(pages)} candidates needing pattern backfill.")

    success_count = 0
    
    for p in pages:
        cand_id = p['id']
        props = client.extract_properties(p)
        name = props.get('이름') or props.get('name') or "Unknown"
        
        logger.info(f"[*] Processing: {name}")
        
        full_text = db.fetch_candidate_details(cand_id)
        if not full_text:
            logger.warning(f"No content found for {name}. Using summary if available.")
            full_text = props.get('experience_summary', '')
            
        if not full_text:
            logger.warning(f"Skipping {name} due to lack of text.")
            continue
            
        parsed = parser.parse(full_text)
        if not parsed:
            logger.error(f"Failed to parse {name}")
            continue
            
        patterns = parsed.get('patterns', [])
        
        safe_patterns_to_upload = set()
        
        for pt in patterns:
            raw_pt = pt.get("verb_object", "").strip().replace(",", " ")
            if raw_pt:
                safe_pt = add_pattern_safe_dynamic(raw_pt, existing_patterns, max_limit=90)
                safe_patterns_to_upload.add(safe_pt)
                
                if safe_pt not in existing_patterns:
                    existing_patterns.append(safe_pt)
                    
        if safe_patterns_to_upload:
            update_props = {
                "Functional Patterns": {"multi_select": [{"name": s[:100]} for s in list(safe_patterns_to_upload)[:20]]}
            }
            try:
                client.update_page_properties(cand_id, update_props)
                logger.info(f"  ✅ Updated {name} with {len(safe_patterns_to_upload)} patterns. Total unique: {len(existing_patterns)}")
                success_count += 1
            except Exception as e:
                logger.error(f"  ❌ Failed to update {name}: {e}")
        else:
            logger.info(f"  ⚠️ No patterns detected for {name}")

    logger.info(f"Backfill complete. Updated {success_count}/{len(pages)} candidates.")
    logger.info(f"Final unique patterns count: {len(existing_patterns)}")

if __name__ == "__main__":
    run_pattern_backfill()
