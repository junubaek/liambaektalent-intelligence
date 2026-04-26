import requests
import json

url = "http://localhost:8000/api/search-v5"

payload = {
  "prompt": "자금 담당자 찾아줘",
  "sectors": [],
  "seniority": "All",
  "required": [],
  "preferred": [],
  "strict_required": False
}

try:
    print("Testing specific query...")
    r = requests.post(url, json=payload, timeout=20)
    print("Status code:", r.status_code)
    data = r.json()
    if r.status_code == 200:
        total = data.get("total", 0)
        print("Success! Total results:", total)
        print("Cands:", len(data.get("candidates", [])))
    else:
        print("Error content:", r.text)
except Exception as e:
    print("Error connecting to backend:", e)
