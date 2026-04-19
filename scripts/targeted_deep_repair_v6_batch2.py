
import os
import json
import time
import sys

PROJECT_ROOT = r"C:\Users\cazam\Downloads\이력서자동분석검색시스템"
sys.path.append(PROJECT_ROOT)

from connectors.gemini_api import GeminiClient
from connectors.notion_api import NotionClient
from resume_parser import ResumeParser
from unified_rebuild_and_sync import extract_text, CANONICAL_MAIN_SECTORS, CANONICAL_SUB_SECTORS

def get_config():
    with open(os.path.join(PROJECT_ROOT, "secrets.json"), "r") as f:
        return json.load(f)

def run_ultra_deep_repair_batch2():
    secrets = get_config()
    gemini = GeminiClient(secrets["GEMINI_API_KEY"])
    notion = NotionClient(secrets["NOTION_API_KEY"])
    db_id = secrets["NOTION_DATABASE_ID"]
    
    # Batch 2 targets and their confirmed .docx paths
    targets = {
        "황인철": r"C:\Users\cazam\Downloads\02_resume_converted_v8\황인철(RF Design & Lab)부문_원본.docx",
        "황보민": r"C:\Users\cazam\Downloads\02_resume_converted_v8\황보민(총무팀 자산관리)부문_원본.docx",
        "홍창윤": r"C:\Users\cazam\Downloads\02_resume_converted_v8\홍창윤(Cloud기술 컨설팅)부문_원본.docx",
        "한정수": r"C:\Users\cazam\Downloads\02_resume_converted_v8\한정수(온라인(퍼포먼스) 마케터)부문_원본.docx",
        "한영빈": r"C:\Users\cazam\Downloads\02_resume_converted_v8\한영빈(디자이너)부문_원본.docx"
    }

    print(f"🚀 Starting ULTRA-DEEP repair for BATCH 2 ({len(targets)} candidates)...")

    for name, path in targets.items():
        if not os.path.exists(path):
            print(f"  ❌ File not found: {path}")
            continue

        print(f"[*] Deep Analysis for: {name}")
        text = extract_text(path)
        
        # Enhanced Prompt for maximum accuracy
        prompt = f"""
You are the most senior AI Talent Analyst. This is a critical audit for BATCH 2.
Analyze the following resume and extract the professional profile with CATEGORICAL PRECISION.

[CRITICAL RULES]
1. Read the ENTIRE document. Many candidates have their latest/most relevant experience in the second half.
2. Main Sectors MUST be chosen ONLY from this list: {CANONICAL_MAIN_SECTORS}
3. Sub Sectors MUST be chosen ONLY from this list: {CANONICAL_SUB_SECTORS}
4. DO NOT HALLUCINATE.
   - If they are an 'RF Design' engineer, they are [HW (Hardware)] -> [회로설계(PCB)] or similar.
   - If they are 'Cloud Consulting', they are [SW (Software)] -> [인프라_Cloud].
   - If they are 'Performance Marketer', they are [마케팅 (Marketing)] -> [퍼포먼스].
   - If they are 'Asset Management' (Property/IT), they are [총무 (General Affairs)] -> [자산관리(부동산; 법인자산; IT 비품 구매 및 관리)].

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
            parsed_data = gemini.get_chat_completion_json(prompt, model="gemini-2.5-flash")
            if not parsed_data:
                print(f"  ❌ AI failed for {name}")
                continue

            profile = parsed_data.get("candidate_profile", {})
            patterns = parsed_data.get("patterns", [])
            
            # Map sectors
            main_sectors = [{"name": s.strip()} for s in profile.get("main_sectors", []) if s.strip() in CANONICAL_MAIN_SECTORS]
            sub_sectors = [{"name": s.strip()} for s in profile.get("sub_sectors", []) if s.strip() in CANONICAL_SUB_SECTORS]
            
            exp_summary = profile.get("experience_summary", "")
            if isinstance(exp_summary, list): exp_summary = "\n".join(exp_summary)

            props = {
                "Main Sectors": {"multi_select": main_sectors},
                "Sub Sectors": {"multi_select": sub_sectors},
                "Experience Summary": {"rich_text": [{"text": {"content": exp_summary[:2000]}}]},
                "Context Tags": {"rich_text": [{"text": {"content": ", ".join(profile.get("context_tags", []))[:2000]}}]},
                "Functional Patterns": {"multi_select": [{"name": p.get("verb_object", "").replace(",", "/").strip()[:100]} for p in patterns if p.get("verb_object", "").strip()]},
                "Seniority Bucket": {"select": {"name": (profile.get("seniority_bucket") or "Unknown")}},
                "AI Last Optimized": {"date": {"start": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}}
            }

            # Find in Notion
            # Try searching by name specifically
            res = notion.query_database(db_id, filter_criteria={"property": "이름", "title": {"contains": name}})
            pages = res.get('results', [])
            
            if pages:
                # Update existing
                page_id = pages[0]['id']
                notion.update_page_properties(page_id, props)
                print(f"  ✅ Updated matching page for {name}")
            else:
                # Create new 
                props["이름"] = {"title": [{"text": {"content": name}}]}
                notion.create_page(db_id, props)
                print(f"  ✨ Created NEW page for {name}")

        except Exception as e:
            print(f"  ❌ Error processing {name}: {e}")

if __name__ == "__main__":
    run_ultra_deep_repair_batch2()
