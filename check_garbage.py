import sqlite3

def check_garbage():
    conn = sqlite3.connect('candidates.db')
    cur = conn.cursor()
    
    cur.execute("SELECT id, name_kr, document_hash FROM candidates WHERE name_kr LIKE '~%' OR name_kr='미상'")
    rows = cur.fetchall()
    print(f'Garbage/Unknown candidates: {len(rows)}')
    for r in rows[:10]:
        print(r)
        
    # Delete them
    if True: # Let's just delete them here
        cur.execute("DELETE FROM candidates WHERE name_kr LIKE '~%'")
        conn.commit()
        print("Deleted ~ temp files from SQLite.")
        
    conn.close()

if __name__ == '__main__':
    check_garbage()
