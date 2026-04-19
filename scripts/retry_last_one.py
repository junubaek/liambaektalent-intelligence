
import os
import json
import sys

PROJECT_ROOT = r"C:\Users\cazam\Downloads\이력서자동분석검색시스템"
if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)

from connectors.gemini_api import GeminiClient
from connectors.notion_api import NotionClient
from unified_rebuild_and_sync import extract_text, CANONICAL_MAIN_SECTORS, CANONICAL_SUB_SECTORS

def run_single_retry():
    with open(os.path.join(PROJECT_ROOT, "secrets.json"), "r") as f:
        secrets = json.load(f)
    
    gemini = GeminiClient(secrets["GEMINI_API_KEY"])
    notion = NotionClient(secrets["NOTION_API_KEY"])
    
    name = "[NC] 전수형(투자담당자)부문"
    page_id = "31f22567-1b6f-8143-a67f-cbbfd21331ab"
    # CORRECT PATH
    path = r"C:\Users\cazam\Downloads\02_resume 전처리\[NC] 전수형(투자담당자)부문.docx"
    
    print(f"[*] Retrying {name} using {path}...")
    text = extract_text(path)
    if not text:
        print("❌ Still failed to extract text.")
        return
        
    prompt = f"""
Analyze this resume.
[CRITICAL RULES]
- Main Sectors ONLY: {CANONICAL_MAIN_SECTORS}
- Sub Sectors ONLY: {CANONICAL_SUB_SECTORS}
[RESUME]
{text}
"""
    parsed_data = gemini.get_chat_completion_json(prompt, model="gemini-1.5-pro")
    
    if parsed_data:
        profile = parsed_data.get("candidate_profile", {})
        main_sectors = [{"name": s.strip()} for s in profile.get("main_sectors", []) if s.strip() in CANONICAL_MAIN_SECTORS]
        sub_sectors = [{"name": s.strip()} for s in profile.get("sub_sectors", []) if s.strip() in CANONICAL_SUB_SECTORS]
        
        props = {
            "Main Sectors": {"multi_select": main_sectors},
            "Sub Sectors": {"multi_select": sub_sectors},
            "Experience Summary": {"rich_text": [{"text": {"content": profile.get("experience_summary", "")[:2000]}}]},
            "Context Tags": {"rich_text": [{"text": {"content": ", ".join(profile.get("context_tags", []))[:2000]}}]}
        }
        notion.update_page_properties(page_id, props)
        print("✅ Success!")
    else:
        print("❌ Still failed.")

if __name__ == "__main__":
    run_single_retry()
