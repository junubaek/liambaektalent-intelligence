import sqlite3
import json
from collections import Counter
import sys
import os

# Add parent directory to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from headhunting_engine.normalization.pattern_merger import PatternMerger

DB_PATH = "c:/Users/cazam/Downloads/안티그래비티/headhunting_engine/data/analytics.db"

def audit():
    print("🔎 Auditing Pattern Distribution (v6.3.6)...")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT data_json FROM candidate_snapshots")
    rows = cursor.fetchall()
    
    merger = PatternMerger()
    
    raw_counter = Counter()
    merged_counter = Counter()
    
    for (data_json,) in rows:
        try:
            data = json.loads(data_json)
            patterns = [p.get("pattern", "") for p in data.get("patterns", [])]
            
            for p in patterns:
                raw_counter[p] += 1
                m = merger.merge(p)
                if m:
                    merged_counter[m] += 1
        except:
            continue
            
    print("\n--- Top 20 Raw Patterns ---")
    for p, count in raw_counter.most_common(20):
        print(f"{count: <5} | {p}")
        
    print("\n--- Top 20 Strategic Clusters (Merged) ---")
    for p, count in merged_counter.most_common(20):
        print(f"{count: <5} | {p}")
        
    print(f"\nTotal Unique Raw: {len(raw_counter)}")
    print(f"Total Unique Merged Clusters: {len(merged_counter)}")
    
    conn.close()

if __name__ == "__main__":
    audit()
