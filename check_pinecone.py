import json
import urllib.request
import traceback

try:
    with open("secrets.json", "r") as f:
        secrets = json.load(f)
        
    host = secrets.get("PINECONE_HOST", "").rstrip("/")
    if not host.startswith("https://"):
        host = f"https://{host}"
        
    url = f"{host}/describe_index_stats"
    req = urllib.request.Request(url, headers={
        "Api-Key": secrets["PINECONE_API_KEY"],
        "Accept": "application/json"
    })
    
    with urllib.request.urlopen(req) as response:
        data = json.loads(response.read().decode('utf-8'))
        print(json.dumps(data, indent=2))
except Exception as e:
    print(traceback.format_exc())
