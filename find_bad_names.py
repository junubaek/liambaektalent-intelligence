import sqlite3

def find_candidate_names():
    conn = sqlite3.connect('candidates.db')
    cur = conn.cursor()
    cur.execute('''
        SELECT name_kr, raw_text
        FROM candidates 
        WHERE name_kr LIKE '%여기어때%' OR name_kr LIKE '%자동화제%'
    ''')
    items = cur.fetchall()
    
    for row in items:
        name_kr, raw = row
        print(f"--- {name_kr} ---")
        print(raw[:300] if raw else 'NO TEXT')
        
    conn.close()

if __name__ == '__main__':
    find_candidate_names()
