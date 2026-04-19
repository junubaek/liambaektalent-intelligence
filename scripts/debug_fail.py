
import json
import os
import sys

BASE_PATH = r"C:\Users\cazam\Downloads\이력서자동분석검색시스템"
sys.path.insert(0, BASE_PATH)

from resume_parser import ResumeParser
from connectors.gemini_api import GeminiClient
from unified_rebuild_and_sync import extract_text, CANONICAL_MAIN_SECTORS

def debug_one_fail():
    secrets_path = os.path.join(BASE_PATH, "secrets.json")
    with open(secrets_path, "r", encoding="utf-8") as f:
        secrets = json.load(f)
    
    client = GeminiClient(secrets["GEMINI_API_KEY"])
    parser = ResumeParser(client)
    
    # Target file
    target_name = "[스타비젼] 김승현(해외영업(B2B)_과장급)부문"
    DIR_CONV_V8 = r"C:\Users\cazam\Downloads\02_resume_converted_docx"
    target_path = os.path.join(DIR_CONV_V8, target_name + ".docx")
    
    if not os.path.exists(target_path):
        print("Path not found, trying fuzzy search...")
        # (Simplified fuzzy for debug)
        for f in os.listdir(DIR_CONV_V8):
            if "김승현" in f:
                target_path = os.path.join(DIR_CONV_V8, f)
                break

    print(f"\n📂 Debugging File: {target_path}")
    text = extract_text(target_path)
    print(f"--- TEXT PREVIEW (500 chars) ---\n{text[:500]}\n---")
    
    parsed = parser.parse(text)
    print(f"RAW AI OUTPUT: {json.dumps(parsed, indent=2, ensure_ascii=False)}")

if __name__ == "__main__":
    debug_one_fail()
