import os
import json
import logging
import urllib.request
import urllib.error
import sys
import difflib

# Add project root to path
PROJECT_ROOT = r"C:\Users\cazam\Downloads\이력서자동분석검색시스템"
sys.path.append(PROJECT_ROOT)

from connectors.notion_api import HeadhunterDB
from connectors.gemini_api import GeminiClient
from resume_parser import ResumeParser

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def add_pattern_safe_dynamic(new_pattern: str, existing_patterns: list, max_limit=90) -> str:
    """Safe addition of patterns respecting the specified max limit."""
    if len(existing_patterns) >= max_limit:
        matches = difflib.get_close_matches(new_pattern, existing_patterns, n=1, cutoff=0.3)
        return matches[0] if matches else (existing_patterns[0] if existing_patterns else new_pattern)
    return new_pattern

def direct_notion_request(method, url, token, payload=None):
    """Bypasses any wrappers to make a strict urllib call that loudly fails."""
    headers = {
        "Authorization": f"Bearer {token}",
        "Notion-Version": "2022-06-28",
        "Content-Type": "application/json"
    }
    data = json.dumps(payload).encode('utf-8') if payload else None
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    
    try:
        with urllib.request.urlopen(req) as response:
            return json.loads(response.read().decode('utf-8')), response.status
    except urllib.error.HTTPError as he:
        err_msg = he.read().decode('utf-8')
        logger.error(f"HTTP {he.code} Error: {err_msg}")
        return None, he.code
    except Exception as e:
        logger.error(f"Network Error: {e}")
        return None, 500

def run_pattern_backfill():
    secrets_path = os.path.join(PROJECT_ROOT, "secrets.json")
    with open(secrets_path, "r", encoding="utf-8") as f:
        secrets = json.load(f)
        
    token = secrets["NOTION_API_KEY"]
    db_id = secrets["NOTION_DATABASE_ID"]
    
    # Init Gemini only
    gemini = GeminiClient(secrets["GEMINI_API_KEY"])
    parser = ResumeParser(gemini)
    
    # Use full DB connector just for fetching text easily
    db = HeadhunterDB(secrets_path)

    # 1. Fetch Existing Patterns explicitly
    logger.info("Fetching existing Functional Patterns schema from Notion...")
    existing_patterns = []
    
    schema_res, status = direct_notion_request("GET", f"https://api.notion.com/v1/databases/{db_id}", token)
    if status == 200 and schema_res and "properties" in schema_res and "Functional Patterns" in schema_res["properties"]:
        options = schema_res["properties"]["Functional Patterns"].get("multi_select", {}).get("options", [])
        existing_patterns = [opt["name"] for opt in options]
        logger.info(f"Loaded {len(existing_patterns)} existing patterns. Limit set to 90.")
    else:
        logger.error(f"Failed to fetch schema. Status: {status}")
        return

    # 2. Query All Candidates without patterns
    logger.info("Querying candidates missing Functional Patterns...")
    filter_empty = {
        "filter": {
            "property": "Functional Patterns",
            "multi_select": {"is_empty": True}
        },
        "page_size": 100
    }
    
    query_res, status = direct_notion_request("POST", f"https://api.notion.com/v1/databases/{db_id}/query", token, filter_empty)
    if status != 200 or not query_res:
         logger.error(f"Failed to fetch candidates. Status: {status}")
         return
         
    pages = query_res.get('results', [])
    logger.info(f"Found {len(pages)} candidates needing pattern backfill.")

    success_count = 0
    
    for p in pages:
        cand_id = p['id']
        name_prop = p["properties"].get("Name", {}).get("title", [])
        name = name_prop[0]["plain_text"] if name_prop else "Unknown"
        
        logger.info(f"[*] Processing: {name}")
        
        full_text = db.fetch_candidate_details(cand_id)
        if not full_text:
            logger.warning(f"No content found for {name}. Using summary if available.")
            summary_prop = p["properties"].get("Experience_Summary", {}).get("rich_text", [])
            full_text = "".join([t["plain_text"] for t in summary_prop]) if summary_prop else ""
            
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
            update_payload = {
                "properties": {
                    "Functional Patterns": {
                        "multi_select": [{"name": s[:100]} for s in list(safe_patterns_to_upload)[:20]]
                    }
                }
            }
            res, status = direct_notion_request("PATCH", f"https://api.notion.com/v1/pages/{cand_id}", token, update_payload)
            if status == 200:
                logger.info(f"  ✅ Updated {name} with {len(safe_patterns_to_upload)} patterns. Total unique schema keys: {len(existing_patterns)}")
                success_count += 1
            else:
                logger.error(f"  ❌ Failed to update {name}. Status {status}")
                # We stop on error to avoid silent fails and quota burn
                break
        else:
            logger.info(f"  ⚠️ No patterns detected for {name}")

    logger.info(f"Backfill complete. Updated {success_count} candidates.")
    logger.info(f"Final unique patterns count: {len(existing_patterns)}")

if __name__ == "__main__":
    run_pattern_backfill()
