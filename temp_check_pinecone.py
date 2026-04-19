import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import json
import logging
import traceback
from connectors.pinecone_api import PineconeClient
import requests

def check_history_stats():
    try:
        with open("secrets.json", "r") as f:
            secrets = json.load(f)
        
        pc_host = secrets.get("PINECONE_HOST", "")
        if not pc_host.startswith("https://"):
            pc_host = f"https://{pc_host}"
        api_key = secrets["PINECONE_API_KEY"]
        pc = PineconeClient(api_key, pc_host)
        
        print("Pinecone API Key available:", bool(api_key))
        print("Pinecone Host:", pc_host)
        
        # Connectors PineconeClient might not have describe_index_stats
        # Let's make a direct HTTP request to Pinecone REST API for stats
        headers = {
            "Api-Key": api_key,
            "Accept": "application/json",
            "Content-Type": "application/json"
        }
        
        url = f"{pc_host}/describe_index_stats"
        print(f"Requesting stats from {url}")
        
        response = requests.post(url, headers=headers)
        if response.status_code == 200:
            print("Stats:")
            print(json.dumps(response.json(), indent=2))
        else:
            print(f"Error getting stats: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"Error: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    check_history_stats()
