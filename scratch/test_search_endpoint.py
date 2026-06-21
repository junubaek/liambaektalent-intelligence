from fastapi.testclient import TestClient
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from backend.main import app

client = TestClient(app)

print("=== Testing /api/search-v8 endpoint ===")
payload = {
    "prompt": "CFO",
    "sectors": [],
    "seniority": ["All"],
    "required": [],
    "preferred": []
}

response = client.post("/api/search-v8", json=payload)
print("Status code:", response.status_code)
if response.status_code == 200:
    data = response.json()
    print("Matched count:", len(data.get("matched", [])))
    if data.get("matched"):
        first = data["matched"][0]
        print("First candidate:", first.get("name_kr"), "| Has CEI:", "cei" in first and first["cei"] is not None)
        if "cei" in first:
            print("CEI:", first["cei"])
else:
    print("Response text:", response.text)
