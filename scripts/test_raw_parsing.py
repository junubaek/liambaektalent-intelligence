
import json
import os
import sys

BASE_PATH = r"C:\Users\cazam\Downloads\이력서자동분석검색시스템"
sys.path.insert(0, BASE_PATH)

from resume_parser import ResumeParser
from connectors.gemini_api import GeminiClient
from unified_rebuild_and_sync import extract_text, CANONICAL_MAIN_SECTORS

def test_raw_parsing():
    secrets_path = os.path.join(BASE_PATH, "secrets.json")
    with open(secrets_path, "r", encoding="utf-8") as f:
        secrets = json.load(f)
    
    client = GeminiClient(secrets["GEMINI_API_KEY"])
    parser = ResumeParser(client)
    
    # Take a few files from the converted folder (since we know they are readable)
    DIR_CONV = r"C:\Users\cazam\Downloads\02_resume_converted_docx"
    files = [f for f in os.listdir(DIR_CONV) if f.endswith(".docx")][:3]
    
    for f in files:
        path = os.path.join(DIR_CONV, f)
        print(f"\n📄 Testing: {f}")
        text = extract_text(path)
        parsed = parser.parse(text)
        
        main_sectors = parsed.get("candidate_profile", {}).get("main_sectors", [])
        print(f"  AI Suggestion: {main_sectors}")
        
        valid = []
        for s in main_sectors:
            if s.strip() in CANONICAL_MAIN_SECTORS:
                valid.append(s)
            else:
                print(f"  ❌ Mismatch: '{s}' (Not in canonical list)")
        
        print(f"  Final Valid: {valid}")

if __name__ == "__main__":
    test_raw_parsing()
