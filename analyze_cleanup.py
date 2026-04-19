import sqlite3
import json

def analyze_names():
    conn = sqlite3.connect('candidates.db')
    cur = conn.cursor()
    cur.execute("SELECT name_kr, count(*) as c, group_concat(id) FROM candidates GROUP BY name_kr ORDER BY name_kr")
    rows = cur.fetchall()
    
    # 1. Names that aren't likely human (e.g., common nouns, 4 chars Korean, etc)
    # 2. Names that are duplicated (c > 1)
    
    duplicates = []
    suspicious = []
    
    for row in rows:
        name = row[0]
        cnt = row[1]
        ids = row[2]
        
        if cnt > 1:
            duplicates.append({'name': name, 'count': cnt})
            
        # Very rough heuristics for suspicious
        if len(name) >= 4 and not name.encode().isalpha(): # 4+ char Korean
            suspicious.append(name)
        elif len(name) <= 1:
            suspicious.append(name)
            
    print(f"Total Unique Names: {len(rows)}")
    print(f"Total Duplicated Names: {len(duplicates)}")
    print(f"Top 20 Duplicates: {duplicates[:20]}")
    print(f"Suspicious 4+ Korean names count: {len(suspicious)}")
    print(f"Suspicious samples: {suspicious[:20]}")

if __name__ == '__main__':
    analyze_names()
