import json
import urllib.request
import urllib.error

def test_gemini_models():
    with open('secrets.json', 'r', encoding='utf-8') as f:
        secrets = json.load(f)
    api_key = secrets['GEMINI_API_KEY']
    
    models = ["models/gemini-1.5-flash", "models/gemini-2.0-flash-exp", "models/gemini-1.5-pro"]
    
    for m in models:
        url = f"https://generativelanguage.googleapis.com/v1beta/{m}:generateContent?key={api_key}"
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
            # If 404, try v1
            if isinstance(e, urllib.error.HTTPError) and e.code == 404:
                url_v1 = f"https://generativelanguage.googleapis.com/v1/{m}:generateContent?key={api_key}"
                try:
                    req = urllib.request.Request(url_v1, data=data, headers=headers)
                    with urllib.request.urlopen(req, timeout=10) as response:
                        print(f"Model {m} (v1): SUCCESS")
                        continue
                except Exception as e2:
                    print(f"Model {m} (v1): FAILED - {e2}")
            print(f"Model {m}: FAILED - {e}")

if __name__ == "__main__":
    test_gemini_models()
