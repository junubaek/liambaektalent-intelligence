import json
import sys
import os

PROJECT_ROOT = r"C:\Users\cazam\Downloads\이력서자동분석검색시스템"
sys.path.append(PROJECT_ROOT)

from connectors.gemini_api import GeminiClient

def test_gemini():
    try:
        with open(os.path.join(PROJECT_ROOT, "secrets.json"), "r") as f:
            secrets = json.load(f)
            
        client = GeminiClient(secrets["GEMINI_API_KEY"])
        res = client.get_chat_completion_json('{"test": "hello"}', model="gemini-2.0-flash")
        if res:
            print("SUCCESS: Quota is fine.")
            print("Response:", res)
        else:
            print("FAILED: Quota might still be exhausted.")
    except Exception as e:
        print("Error:", e)

if __name__ == "__main__":
    test_gemini()
