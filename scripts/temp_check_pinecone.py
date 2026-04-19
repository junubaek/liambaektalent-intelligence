import json
import logging
import traceback
from connectors.pinecone_api import PineconeClient

def check_history_stats():
    try:
        with open("secrets.json", "r") as f:
            secrets = json.load(f)
        
        pc_host = secrets.get("PINECONE_HOST", "")
        if not pc_host.startswith("https://"):
            pc_host = f"https://{pc_host}"
        pc = PineconeClient(secrets["PINECONE_API_KEY"], pc_host)
        
        # We need to query or get stats
        print("Pinecone API Key available:", bool(secrets.get("PINECONE_API_KEY")))
        print("Pinecone Host:", pc_host)
        
        # We don't have direct access to index stats via PineconeClient in connectors without looking at it.
        # Let's inspect the client methods.
        print("PineconeClient attributes:", dir(pc))
    except Exception as e:
        print(f"Error: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    check_history_stats()
