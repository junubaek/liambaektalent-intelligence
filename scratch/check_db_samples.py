import sqlite3

def check_db_count():
    conn = sqlite3.connect('candidates.db')
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM candidates")
    print(f"Total candidates: {cursor.fetchone()[0]}")
    
    cursor.execute("SELECT id, name_kr FROM candidates LIMIT 20")
    rows = cursor.fetchall()
    print("Sample candidates:")
    for row in rows:
        print(f"ID: {row[0]}, Name: {row[1]}")
        
    conn.close()

if __name__ == "__main__":
    check_db_count()
