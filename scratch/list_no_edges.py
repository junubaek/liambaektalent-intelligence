import sqlite3
import json

def list_no_edges():
    conn = sqlite3.connect('candidates.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Candidates who are "parsed" but have no actual career patterns (edges)
    query = """
    SELECT id, name_kr, email, current_company
    FROM candidates 
    WHERE is_duplicate = 0 
      AND is_parsed = 1
      AND (careers_json IS NULL OR careers_json = '[]' OR careers_json = '')
    LIMIT 20
    """
    rows = cursor.execute(query).fetchall()
    
    print("=== Candidates with No Career Patterns (No Edges) ===")
    for row in rows:
        print(f"ID: {row['id']}")
        print(f"Name: {row['name_kr']}")
        print(f"Email: {row['email'] or 'N/A'}")
        print(f"Company: {row['current_company'] or 'N/A'}")
        print("-" * 20)
        
    cursor.execute("SELECT COUNT(*) FROM candidates WHERE is_duplicate = 0 AND is_parsed = 1 AND (careers_json IS NULL OR careers_json = '[]' OR careers_json = '')")
    total = cursor.fetchone()[0]
    print(f"\nTotal Candidates with no edges: {total}")
    
    conn.close()

if __name__ == "__main__":
    list_no_edges()
