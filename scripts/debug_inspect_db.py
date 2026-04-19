import sqlite3
import json
import os

DB_PATH = "headhunting_engine/data/analytics.db"

def inspect():
    conn = sqlite3.connect(DB_PATH)
    row = conn.execute("SELECT data_json FROM candidate_snapshots WHERE data_json IS NOT NULL LIMIT 1").fetchone()
    if row:
        data = json.loads(row[0])
        print(f"Keys: {list(data.keys())}")
        if "candidate_profile" in data:
            print(f"Profile Keys: {list(data['candidate_profile'].keys())}")
        if "gdrive_link" in data:
            print(f"GDrive Link Found: {data['gdrive_link']}")
        else:
            print("GDrive Link NOT found in top level.")
        
        print("\nFull Data (first 1000 chars):")
        print(json.dumps(data, indent=2, ensure_ascii=False)[:1000])
    else:
        print("No data found.")
    conn.close()

if __name__ == "__main__":
    inspect()
