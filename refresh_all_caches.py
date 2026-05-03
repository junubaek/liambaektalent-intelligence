import os
import subprocess
import json
import sqlite3
import time
from neo4j import GraphDatabase

def run_script(name):
    print(f"Running {name}...")
    try:
        subprocess.run(["python", name], check=True)
        print(f"Successfully finished {name}.")
    except Exception as e:
        print(f"Error running {name}: {e}")

def main():
    print("=== Talent Intelligence OS Cache Refresh Tool ===")
    
    # 1. Rebuild BM25 Index
    if os.path.exists("build_bm25_index.py"):
        run_script("build_bm25_index.py")
    else:
        print("Warning: build_bm25_index.py not found.")

    # 2. Re-expand Embeddings (Optional, but user already did it)
    # run_script("run_neo4j_embedding_expansion.py")

    # 3. Handle candidates_cache_jd.json
    # If it exists, it might contain stale data. We can either delete it 
    # to force DB fallback or refresh it from SQLite.
    cache_path = "candidates_cache_jd.json"
    if os.path.exists(cache_path):
        print(f"Backing up and removing stale {cache_path}...")
        os.rename(cache_path, f"{cache_path}.bak_{int(time.time())}")
        print(f"Stale cache removed. Search engine will now use latest SQLite data.")

    # 4. Clear Backend Cache (Instructions)
    print("\n[NOTE] Backend Cache (jd_cache) is in-memory.")
    print("If you are running the FastAPI server, please restart it to clear the cache.")
    print("Alternatively, you can run 'python -c \"import backend.main; backend.main.jd_cache.clear()\"' if the process allows.")

    print("\n=== All cache refresh tasks completed. ===")

if __name__ == "__main__":
    main()
