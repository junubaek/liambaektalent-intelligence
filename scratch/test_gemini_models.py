import json
import urllib.request
import urllib.error

def test_gemini_models():
    with open('secrets.json', 'r', encoding='utf-8') as f:
        secrets = json.load(f)
    api_key = secrets['GEMINI_API_KEY']
    
    models = ["gemini-2.0-flash-exp", "gemini-1.5-flash", "gemini-2.0-flash"]
    
    for m in models:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{m}:generateContent?key={api_key}"
        payload = {
            "contents": [{"parts": [{"text": "Say hello"}]}]
        }
        data = json.dumps(payload).encode('utf-8')
        headers = {"Content-Type": "application/json"}
        
        try:
            req = urllib.request.Request(url, data=data, headers=headers)
            with urllib.request.urlopen(req, timeout=10) as response:
                print(f"Model {m}: SUCCESS")
        except Exception as e:
            print(f"Model {m}: FAILED - {e}")

if __name__ == "__main__":
    test_gemini_models()
