import sqlite3
import os

def analyze_candidates_v2():
    conn = sqlite3.connect('candidates.db')
    conn.row_factory = sqlite3.Row
    
    # Names to search for
    target_names = ['백민종', '정진숙', '배정석']
    
    for name in target_names:
        print(f"=== Searching for: {name} ===")
        # Search in name_kr (even if it looks garbled) and raw_text
        query = "SELECT id, name_kr, email, current_company, sector, raw_text FROM candidates WHERE name_kr LIKE ? OR raw_text LIKE ?"
        rows = conn.cursor().execute(query, (f'%{name}%', f'%{name}%')).fetchall()
        
        if not rows:
            print("No matches found.")
            continue
            
        for row in rows:
            print(f"--- ID: {row['id']} ---")
            # Handle garbled name display
            try:
                name_kr = row['name_kr']
                print(f"Name_KR: {name_kr}")
            except:
                print("Name_KR: [Encoding Error]")
                
            print(f"Email: {row['email']}")
            print(f"Current Company: {row['current_company']}")
            
            # Print raw text snippet to stdout using utf-8 if possible, else replace
            raw_text = row['raw_text'] if row['raw_text'] else ""
            # Safely print snippet
            snippet = raw_text[:500].replace('\n', ' ')
            print(f"Raw Text Snippet: {snippet.encode('ascii', 'replace').decode('ascii')}")
            print("")
            
    conn.close()

if __name__ == "__main__":
    analyze_candidates_v2()
