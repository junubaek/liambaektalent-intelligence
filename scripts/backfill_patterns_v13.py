import os
import json
import logging
import urllib.request
import urllib.error
import sys
import time
import re

PROJECT_ROOT = r"C:\Users\cazam\Downloads\이력서자동분석검색시스템"
sys.path.append(PROJECT_ROOT)

from connectors.notion_api import HeadhunterDB
from connectors.gemini_api import GeminiClient

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def direct_notion_request(method, url, token, payload=None, retries=3):
    headers = {
        "Authorization": f"Bearer {token}",
        "Notion-Version": "2022-06-28",
        "Content-Type": "application/json"
    }
    data = json.dumps(payload).encode('utf-8') if payload else None
    
    for attempt in range(retries):
        req = urllib.request.Request(url, data=data, headers=headers, method=method)
        try:
            with urllib.request.urlopen(req) as response:
                return json.loads(response.read().decode('utf-8')), response.status
        except urllib.error.HTTPError as he:
            logger.error(f"HTTP {he.code} Error: {he.read().decode('utf-8')}")
            if he.code in [400, 401, 403, 404]:
                return None, he.code # Non-retriable usually
        except Exception as e:
            logger.error(f"Network Error on attempt {attempt+1}: {e}")
            
        time.sleep(2 * (attempt + 1))
        
    return None, 500

def run_backfill():
    secrets_path = os.path.join(PROJECT_ROOT, "secrets.json")
    with open(secrets_path, "r", encoding="utf-8") as f:
        secrets = json.load(f)
        
    token = secrets["NOTION_API_KEY"]
    db_id = secrets["NOTION_DATABASE_ID"]
    gemini = GeminiClient(secrets["GEMINI_API_KEY"])
    db = HeadhunterDB(secrets_path)

    # 1. Fetch Existing Patterns schema to pass to AI for reference
    schema_res, status = direct_notion_request("GET", f"https://api.notion.com/v1/databases/{db_id}", token)
    existing_keys = []
    if status == 200 and schema_res:
        opts = schema_res["properties"]["Functional Patterns"].get("multi_select", {}).get("options", [])
        existing_keys = [opt["name"] for opt in opts]
    
    # Send a small sample (max 100) to the prompt to give it context of our standardized patterns
    sample_keys = existing_keys[:100]

    PROMPT_TEMPLATE = """
You are an expert Talent Intelligence AI extracting 'Functional Patterns' from a candidate's resume text.

[RULES FOR EXTRACTION]
1. EXCLUDE EMOTION & SUBJECTIVITY: We only care ABOUT what they were exposed to, not how well they did it.
2. EXCLUDE PERFORMANCE NUMBERS: No metrics like "20,000 users".
3. STANDARDIZED FACTUAL FORMAT: Every pattern MUST be in English and end with one of these suffixes: `_Exp`, `_Env`, `_Process`, `_Cycle`.
4. USE SNAKE_CASE: Connect everything with underscores. No commas. No spaces. e.g. `Marketing_Data_Analysis_Exp`.
5. REUSE IF POSSIBLE: If your extracted concept matches any of our existing schema patterns, use the exact schema pattern string! 

[EXISTING PATTERN SCHEMA (SAMPLE)]
{schema}

[CANDIDATE TEXT]
{text}

Return a strictly valid JSON list of strings representing the 5 to 10 most prominent functional patterns from this text.
Do not output markdown code blocks. Just the JSON list. e.g.:
["Data_Pipeline_Dev_Exp", "Server_Cluster_Reconstruction_Exp"]
"""

    has_more = True
    success_count = 0
    
    logger.info("Starting robust fetch of empty candidates (first-page-only)...")
    
    while has_more:
        payload = {"filter": {"property": "Functional Patterns", "rich_text": {"is_empty": True}}, "page_size": 20}
        
        # We DO NOT use next_cursor. Since we are filling the empty fields, 
        # the candidates disappear from this filter automatically.
        # We just keep fetching the first 20 empty ones until none are left!

        res, status = direct_notion_request("POST", f"https://api.notion.com/v1/databases/{db_id}/query", token, payload)
        if status != 200 or not res:
            logger.error(f"Failed to query Notion candidates. Status: {status}. Automatically retrying in 10s...")
            time.sleep(10)
            continue
            
        pages = res.get("results", [])
        if not pages:
            logger.info("No more empty candidates found!")
            break
        
        for p in pages:
            cand_id = p["id"]
            name_prop = p["properties"].get("Name", {}).get("title", [])
            name = name_prop[0]["plain_text"] if name_prop else "Unknown"
            
            logger.info(f"[*] Processing: {name}")
            full_text = ""
            try:
                full_text = db.fetch_candidate_details(cand_id)
            except Exception as e:
                logger.error(f"  ❌ Failed to fetch text from Notion for {name}: {e}")

            if not full_text:
                summary_prop = p["properties"].get("Experience_Summary", {}).get("rich_text", [])
                full_text = "".join([t["plain_text"] for t in summary_prop]) if summary_prop else ""
                
            if not full_text:
                logger.warning(f"  ⏭️ Skipping {name}: No text available. Marking as No_Data_Processed.")
                update_payload = {"properties": {"Functional Patterns": {"rich_text": [{"text": {"content": "No_Data_Processed"}}]}}}
                direct_notion_request("PATCH", f"https://api.notion.com/v1/pages/{cand_id}", token, update_payload)
                continue

            prompt = PROMPT_TEMPLATE.format(schema=json.dumps(sample_keys), text=full_text[:30000])
            
            try:
                patterns = gemini.get_chat_completion_json(prompt)
                if not isinstance(patterns, list):
                    logger.warning(f"  ⚠️ AI did not return a list for {name}.")
                    continue
                    
                # Clean up to be safe
                clean_patterns = []
                for pt in patterns:
                    pt_clean = str(pt).strip().replace(",", "/").replace(" ", "_").replace("__", "_")
                    if pt_clean:
                        clean_patterns.append(pt_clean[:100])
                        
                # Limit to top 20 to avoid Notion limit
                clean_patterns = list(set(clean_patterns))[:20]

                if clean_patterns:
                    update_payload = {"properties": {"Functional Patterns": {"rich_text": [{"text": {"content": ", ".join(clean_patterns)}}]}}}
                    patch_res, patch_status = direct_notion_request("PATCH", f"https://api.notion.com/v1/pages/{cand_id}", token, update_payload)
                    
                    if patch_status == 200:
                        logger.info(f"  ✅ Updated {name} with {len(clean_patterns)} standardized patterns.")
                        success_count += 1
                    else:
                        logger.error(f"  ❌ Failed to patch {name}. Status {patch_status}")
                else:
                    logger.info(f"  ⚠️ No valid patterns generated for {name}")

            except Exception as e:
                logger.error(f"  ❌ AI/Parse Error for {name}: {e}")
                
            time.sleep(1) # rate limit

    logger.info(f"Backfill complete! Filled {success_count} candidates.")

if __name__ == "__main__":
    run_backfill()
