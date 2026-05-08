import sqlite3
import json

def check_targets():
    with open('reparse_targets.json', 'r', encoding='utf-8') as f:
        targets = json.load(f)
        
    ids = [t['id'] for t in targets]
    
    conn = sqlite3.connect('candidates.db')
    cursor = conn.cursor()
    
    placeholders = ', '.join(['?'] * len(ids))
    query = f"SELECT id, name_kr, is_parsed, total_years, sector FROM candidates WHERE id IN ({placeholders})"
    
    cursor.execute(query, ids)
    rows = cursor.fetchall()
    
    print(f"{'ID':<40} | {'Name':<10} | {'Parsed':<6} | {'Years':<5} | {'Sector'}")
    print("-" * 80)
    for row in rows:
        print(f"{row[0]:<40} | {row[1]:<10} | {row[2]:<6} | {row[3]:<5} | {row[4]}")
        
    conn.close()

if __name__ == "__main__":
    check_targets()
