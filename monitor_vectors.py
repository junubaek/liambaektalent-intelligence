
import json
import urllib.request
import os

def monitor_pinecone():
    secrets_path = r"C:\Users\cazam\Downloads\안티그래비티\secrets.json"
    if not os.path.exists(secrets_path):
        print("secrets.json not found.")
        return

    with open(secrets_path, "r") as f:
        secrets = json.load(f)
    
    api_key = secrets["PINECONE_API_KEY"]
    host = secrets["PINECONE_HOST"].rstrip("/")
    if not host.startswith("https://"):
        host = f"https://{host}"
    
    url = f"{host}/describe_index_stats"
    headers = {
        "Api-Key": api_key,
        "Accept": "application/json"
    }
    
    req = urllib.request.Request(url, headers=headers)
    
    try:
        with urllib.request.urlopen(req) as response:
            stats = json.load(response)
            total_vectors = stats.get("totalVectorCount", 0)
            print("\n" + "="*40)
            print("🌌 AI Talent Intelligence: Vector Monitor")
            print("="*40)
            print(f"📍 Pinecone Host: {host}")
            print(f"📊 Total Vectors: {total_vectors:,}")
            print(f"🗂️ Namespaces: {list(stats.get('namespaces', {}).keys())}")
            print("="*40 + "\n")
            return stats
    except Exception as e:
        print(f"❌ Error monitoring Pinecone: {e}")
        return None

if __name__ == "__main__":
    monitor_pinecone()
