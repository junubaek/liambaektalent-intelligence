import sqlite3
import os

def analyze_all_targets():
    conn = sqlite3.connect('candidates.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    targets = ['송경석', '방주용', '이우상', '김태형', '류래민']
    
    print("=== Analyzing Candidates ===")
    for target in targets:
        print(f"\nSearching for: {target}")
        # Search in name_kr (LIKE might work if bytes match) or raw_text
        rows = cursor.execute("SELECT id, name_kr, email, current_company, raw_text FROM candidates WHERE name_kr LIKE ? OR raw_text LIKE ?", (f'%{target}%', f'%{target}%')).fetchall()
        
        for row in rows:
            print(f"--- ID: {row['id']} ---")
            print(f"Name_KR (Display): {row['name_kr']}")
            print(f"Email: {row['email']}")
            print(f"Company: {row['current_company']}")
            
            text = row['raw_text'] if row['raw_text'] else ""
            found_names = []
            for name in targets:
                if name in text:
                    found_names.append(name)
            print(f"Found names in text: {found_names}")
            
            # Safe print snippet
            snippet = text[:300].replace('\n', ' ').replace('\r', ' ')
            # Use ascii replace to avoid encoding errors in shell
            print(f"Snippet: {snippet.encode('ascii', 'replace').decode('ascii')}")
            
    conn.close()

if __name__ == "__main__":
    analyze_all_targets()
