import urllib.request
import json

with open("secrets.json", "r") as f:
    api_key = json.load(f)["GEMINI_API_KEY"]

models = ["gemini-2.0-flash-exp", "gemini-1.5-flash", "gemini-2.5-flash"]

for m in models:
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{m}:generateContent?key={api_key}"
    payload = {
        "contents": [{"parts": [{"text": "Hello"}]}],
        "generationConfig": {"response_mime_type": "application/json"}
    }
    data = json.dumps(payload).encode('utf-8')
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req) as response:
            print(f"Success: {m}")
    except Exception as e:
        print(f"Failed {m}: {e}")
