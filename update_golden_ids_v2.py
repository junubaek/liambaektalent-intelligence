
import json
import sqlite3
import os
import sys

# Set output encoding to utf-8
sys.stdout.reconfigure(encoding='utf-8')

def update_golden_ids():
    dataset_path = r'c:\Users\cazam\Downloads\이력서자동분석검색시스템\golden_dataset_v7.json'
    db_path = r'c:\Users\cazam\Downloads\이력서자동분석검색시스템\candidates.db'
    
    with open(dataset_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    
    updated_count = 0
    total_relevant = 0
    
    for item in data:
        names = item.get('relevant_names', [])
        new_ids = []
        for name in names:
            total_relevant += 1
            # Search for this name in current DB
            cur.execute("SELECT id FROM candidates WHERE name_kr = ? ORDER BY LENGTH(COALESCE(raw_text, '')) DESC", (name,))
            rows = cur.fetchall()
            if rows:
                new_ids.append(rows[0][0])
                if rows[0][0] not in item.get('relevant_ids', []):
                    updated_count += 1
            else:
                print(f"Warning: Name {name} not found in current DB.")
        
        # Update relevant_ids
        if new_ids:
            item['relevant_ids'] = new_ids
            
    # Save updated dataset
    output_path = r'c:\Users\cazam\Downloads\이력서자동분석검색시스템\golden_dataset_v7_updated.json'
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        
    print(f"Updated {updated_count} out of {total_relevant} relevant ID mappings.")
    print(f"Saved to {output_path}")
    conn.close()

if __name__ == "__main__":
    update_golden_ids()
