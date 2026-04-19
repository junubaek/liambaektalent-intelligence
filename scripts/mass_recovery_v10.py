
import os
import json
import time
import sys
from concurrent.futures import ThreadPoolExecutor
from functools import partial

PROJECT_ROOT = r"C:\Users\cazam\Downloads\이력서자동분석검색시스템"
sys.path.append(PROJECT_ROOT)

from connectors.gemini_api import GeminiClient
from connectors.notion_api import NotionClient
from unified_rebuild_and_sync import extract_text, CANONICAL_MAIN_SECTORS, CANONICAL_SUB_SECTORS, DIR_RAW, DIR_CONV, DIR_CONV_V8

def get_config():
    with open(os.path.join(PROJECT_ROOT, "secrets.json"), "r") as f:
        return json.load(f)

def find_best_file(name):
    # Search in V8, then CONV, then RAW
    for d in [DIR_CONV_V8, DIR_CONV, DIR_RAW]:
        if not os.path.exists(d): continue
        for f in os.listdir(d):
            if name in f and f.lower().endswith(('.pdf', '.docx')) and not f.startswith('~$'):
                return os.path.join(d, f)
    return None

def repair_single(candidate, gemini, notion, db_id):
    name = candidate['name']
    page_id = candidate['id']
    
    # Try fuzzy name matching if it's structured like "[NC] Name(Role)부문"
    clean_name = name.split('(')[0].split(']')[-1].strip() if '(' in name else name.split(']')[-1].strip()
    
    path = find_best_file(clean_name) or find_best_file(name)
    if not path:
        print(f"  ❌ File not found for {name} (tried '{clean_name}')")
        return False

    print(f"[*] Recovery for {name} using {os.path.basename(path)}")
    text = extract_text(path)
    if len(text) < 100:
        print(f"  ⚠️ Text still too short ({len(text)}) for {name}")
        # Continue anyway, AI might find something
        
    prompt = f"""
You are the most senior AI Talent Analyst. This is a MASS RECOVERY AUDIT.
Analyze the following resume and extract the professional profile with CATEGORICAL PRECISION.
The input text might be structured in columns or tables.

[CRITICAL RULES]
1. Read the ENTIRE document.
2. Main Sectors MUST be chosen ONLY from this list: {CANONICAL_MAIN_SECTORS}
3. Sub Sectors MUST be chosen ONLY from this list: {CANONICAL_SUB_SECTORS}
4. DO NOT HALLUCINATE "incomplete" messages. If you see ANY professional info, categorize it.

[RESUME TEXT]
{text}

[JSON SCHEMA]
{{
  "candidate_profile": {{
    "main_sectors": ["List of Main Sectors"],
    "sub_sectors": ["List of Sub Sectors"],
    "seniority_bucket": "Junior | Middle | Senior",
    "experience_summary": "Extremely detailed summary of their core expertise",
    "context_tags": ["Key technical keywords"]
  }},
  "patterns": [
    {{
      "verb_object": "Action + Achievement pattern",
      "impact": "Quantified result if any"
    }}
  ]
}}
"""
    try:
        parsed_data = gemini.get_chat_completion_json(prompt, model="gemini-3-flash-preview")
        if not parsed_data: return False
        
        # Sometimes Gemini returns a list containing the dict
        if isinstance(parsed_data, list):
            parsed_data = parsed_data[0] if len(parsed_data) > 0 else {}

        profile = parsed_data.get("candidate_profile", {})
        patterns = parsed_data.get("patterns", [])
        
        main_sectors = [{"name": s.strip()} for s in profile.get("main_sectors", []) if s.strip() in CANONICAL_MAIN_SECTORS]
        sub_sectors = [{"name": s.strip()} for s in profile.get("sub_sectors", []) if s.strip() in CANONICAL_SUB_SECTORS]
        
        exp_summary = profile.get("experience_summary", "")
        if isinstance(exp_summary, list): exp_summary = "\n".join(exp_summary)

        props = {
            "Main Sectors": {"multi_select": main_sectors},
            "Sub Sectors": {"multi_select": sub_sectors},
            "Experience Summary": {"rich_text": [{"text": {"content": exp_summary[:2000]}}]},
            "Context Tags": {"rich_text": [{"text": {"content": ", ".join(profile.get("context_tags", []))[:2000]}}]},
            "Functional Patterns": {"multi_select": [{"name": p.get("verb_object", "").strip()[:100]} for p in patterns if p.get("verb_object", "").strip()]},
            "Seniority Bucket": {"select": {"name": (profile.get("seniority_bucket") or "Unknown")}},
            "AI Last Optimized": {"date": {"start": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}}
        }

        notion.update_page_properties(page_id, props)
        print(f"  ✅ Recovered {name}")
        return True
    except Exception as e:
        print(f"  ❌ Error for {name}: {e}")
        return False

def run_mass_recovery():
    secrets = get_config()
    gemini = GeminiClient(secrets["GEMINI_API_KEY"])
    notion = NotionClient(secrets["NOTION_API_KEY"])
    db_id = secrets["NOTION_DATABASE_ID"]
    
    with open("incomplete_list.json", "r", encoding="utf-8") as f:
        targets = json.load(f)

    print(f"🚀 Starting MASS RECOVERY for {len(targets)} candidates...")
    
    # Use ThreadPool to speed up
    with ThreadPoolExecutor(max_workers=5) as executor:
        results = list(executor.map(lambda c: repair_single(c, gemini, notion, db_id), targets))
        
    print(f"\n✨ Mass Recovery Complete. Success: {sum(results)}/{len(targets)}")

if __name__ == "__main__":
    run_mass_recovery()
