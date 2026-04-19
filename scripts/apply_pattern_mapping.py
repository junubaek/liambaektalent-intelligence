import os
import json
import logging
import urllib.request
import urllib.error
import time

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def direct_notion_request(method, url, token, payload=None):
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
        logger.error(f"HTTP {he.code} Error on {method} {url}: {err_msg}")
        return None, he.code
    except Exception as e:
        logger.error(f"Network Error: {e}")
        return None, 500

def run_pattern_cleanup():
    with open("secrets.json", "r", encoding="utf-8") as f:
        secrets = json.load(f)
        
    token = secrets["NOTION_API_KEY"]
    db_id = secrets["NOTION_DATABASE_ID"]

    with open("pattern_mapping.json", "r", encoding="utf-8") as f:
        mapping = json.load(f)

    logger.info(f"Loaded {len(mapping)} mappings.")

    has_more = True
    next_cursor = None
    processed_count = 0
    updated_count = 0
    
    while has_more:
        # We only need to check pages that actually have Patterns
        payload = {
            "filter": {
                "property": "Functional Patterns",
                "multi_select": {
                    "is_not_empty": True
                }
            },
            "page_size": 100
        }
        if next_cursor:
            payload["start_cursor"] = next_cursor

        logger.info(f"Fetching batch. Cursor: {next_cursor}")
        res, status = direct_notion_request("POST", f"https://api.notion.com/v1/databases/{db_id}/query", token, payload)
        
        if status != 200 or not res:
            logger.error(f"Failed to fetch candidates. Status: {status}")
            break
            
        has_more = res.get("has_more", False)
        next_cursor = res.get("next_cursor")
        pages = res.get("results", [])
        
        for p in pages:
            cand_id = p["id"]
            name_prop = p["properties"].get("Name", {}).get("title", [])
            name = name_prop[0]["plain_text"] if name_prop else "Unknown"
            
            raw_options = p["properties"].get("Functional Patterns", {}).get("multi_select", [])
            old_patterns = [opt["name"] for opt in raw_options]
            
            new_pattern_set = set()
            changed = False
            
            for ptrn in old_patterns:
                # Check if it exists in mapping
                # Fallback to current pattern if no exact match (though 99% should match)
                if ptrn in mapping:
                    mapped_ptrn = mapping[ptrn]
                    # Log mapping change for visibility
                    if ptrn != mapped_ptrn:
                        changed = True
                    new_pattern_set.add(mapped_ptrn)
                else:
                    new_pattern_set.add(ptrn)
            
            # Since we use a set, any duplicates created during mapping are inherently merged!
            if len(new_pattern_set) != len(old_patterns):
                changed = True

            processed_count += 1
            
            if changed:
                # Replace with max 100 characters per Notion requirement, and max 100 items
                new_multi_select = [{"name": s[:100].replace(",", "/")} for s in list(new_pattern_set)[:95]]
                
                update_payload = {
                    "properties": {
                        "Functional Patterns": {
                            "multi_select": new_multi_select
                        }
                    }
                }
                patch_res, patch_status = direct_notion_request("PATCH", f"https://api.notion.com/v1/pages/{cand_id}", token, update_payload)
                if patch_status == 200:
                    logger.info(f"  ✅ Updated '{name}': {len(old_patterns)} -> {len(new_pattern_set)} unified patterns.")
                    updated_count += 1
                else:
                    logger.error(f"  ❌ Failed to update '{name}'. Status {patch_status}")
                    
            # Prevent rate limit 3 req/sec
            time.sleep(0.3)
            
    logger.info(f"\nCleanup finished! Processed: {processed_count}, Updated: {updated_count}")

if __name__ == "__main__":
    run_pattern_cleanup()
