import sqlite3

def find_mismatch():
    conn = sqlite3.connect('candidates.db')
    conn.row_factory = sqlite3.Row
    
    # Search for Ryu Laemin in text or Kim Taehyong in name
    query = """
    SELECT id, name_kr, email, current_company, raw_text 
    FROM candidates 
    WHERE raw_text LIKE '%류래민%' 
       OR name_kr LIKE '%김태형%'
       OR name_kr LIKE '%류래민%'
    """
    rows = conn.cursor().execute(query).fetchall()
    
    print(f"Found {len(rows)} potential matches.")
    for row in rows:
        print(f"--- ID: {row['id']} ---")
        print(f"Name_KR: {row['name_kr']}")
        print(f"Email: {row['email']}")
        print(f"Company: {row['current_company']}")
        # Check if text contains Ryu Laemin
        text = row['raw_text'] if row['raw_text'] else ""
        if '류래민' in text:
            print("  [INFO] Raw text contains '류래민'")
        if '김태형' in text:
            print("  [INFO] Raw text contains '김태형'")
        print(f"Text Preview: {text[:200].replace('\n', ' ')}")
        print("")
        
    conn.close()

if __name__ == "__main__":
    find_mismatch()
