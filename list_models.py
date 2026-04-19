
import json
import urllib.request
import os

def list_models():
    secrets_path = r"C:\Users\cazam\Downloads\이력서자동분석검색시스템\secrets.json"
    with open(secrets_path, "r") as f:
        secrets = json.load(f)
    
    api_key = secrets["GEMINI_API_KEY"]
    
    url = f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}"
    
    print(f"Listing models from: {url}")
    try:
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req) as response:
            res = json.loads(response.read().decode('utf-8'))
            print("--- Available Models ---")
            for model in res.get("models", []):
                print(f"- {model['name']} ({model['displayName']})")
    except Exception as e:
        print(f"❌ Failed to list models: {e}")

if __name__ == "__main__":
    list_models()
