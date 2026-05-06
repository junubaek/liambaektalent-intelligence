import sqlite3

def list_the_7():
    conn = sqlite3.connect('candidates.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # The batch limit was 50.
    # We find the 50 most recently 'checked' records (even if not successfully parsed)
    # Actually, my script only updates updated_at on success.
    # So I'll look for records that have is_parsed=0 or empty careers_json but are NOT duplicates.
    
    query = """
    SELECT id, name_kr, email, raw_text
    FROM candidates 
    WHERE is_duplicate = 0 AND is_parsed = 0
    LIMIT 20
    """
    rows = cursor.execute(query).fetchall()
    
    print("Candidates still pending parsing (Potential failures):")
    for row in rows:
        print(f"- {row['name_kr']} ({row['email'] or 'No Email'}) [ID: {row['id']}]")
        
    conn.close()

if __name__ == "__main__":
    list_the_7()
