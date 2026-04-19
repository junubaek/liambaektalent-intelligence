import os
import json
import sqlite3
from connectors.openai_api import OpenAIClient
from matching.hybrid_search_v6_2 import PineconeHybridSearch

# Load Secrets
with open("secrets.json", "r") as f:
    secrets = json.load(f)

OPENAI_KEY = secrets["OPENAI_API_KEY"]
PINECONE_KEY = secrets["PINECONE_API_KEY"]
PINECONE_HOST = secrets["PINECONE_HOST"]
INDEX_NAME = secrets["PINECONE_INDEX_NAME"]

def reindex_pattern(pattern_name: str, sector: str = None):
    print(f"🚀 Triggering Vector Re-scan for pattern: {pattern_name}...")
    
    # Initialize Search
    search = PineconeHybridSearch(PINECONE_KEY, PINECONE_HOST, INDEX_NAME, OPENAI_KEY)
    
    # Query: The pattern name or descriptive text
    # We use vector search to find contextually similar candidates
    results = search.search(pattern_name, limit=50, sector=sector)
    
    print(f"🔍 Found {len(results)} potential matches via Vector Re-scan.")
    
    # In a real scenario, we would tag these candidates or notify the user.
    # For now, we print them as a 'Discovery Match' list.
    for i, res in enumerate(results):
        print(f"  [{i+1}] Candidate: {res['name']} (Score: {res['score']:.4f})")
    
    print("✨ Re-scan complete.")

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        reindex_pattern(sys.argv[1])
    else:
        print("Usage: python scripts/reindex_discovered_pattern.py <pattern_name>")
