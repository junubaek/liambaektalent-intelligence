import sqlite3
import json
import re
import requests

def main():
    conn = sqlite3.connect('candidates.db')
    cur = conn.cursor()
    
    cur.execute("SELECT id, name_kr FROM candidates WHERE name_kr IS NOT NULL")
    rows = cur.fetchall()
    
    print(f"동기화 준비 중... 총 {len(rows)}건")
    
    url = 'http://127.0.0.1:7474/db/neo4j/tx/commit'
    statements = []
    
    for row in rows:
        _id = row[0]
        name_kr = row[1]
        
        query = f"MATCH (c:Candidate {{id: '{_id}'}}) SET c.name_kr = '{name_kr}'"
        statements.append({'statement': query})
    
    # Send in batches of 500
    batch_size = 500
    for i in range(0, len(statements), batch_size):
        batch = statements[i:i+batch_size]
        payload = {'statements': batch}
        res = requests.post(url, json=payload, auth=('neo4j', 'toss1234'))
        if res.status_code == 200:
            print(f"Neo4j 배치 {i} ~ {i+len(batch)} 동기화 완료")
        else:
            print(f"Neo4j 오류:", res.text[:200])
            
    conn.close()
    print("완료되었습니다.")

if __name__ == "__main__":
    main()
