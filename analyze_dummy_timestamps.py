import sqlite3, sys
sys.stdout.reconfigure(encoding='utf-8')

def analyze_timestamps():
    conn = sqlite3.connect('candidates.db')
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    print('=== 1. Dummy ID Prefix & Timestamps ===')
    q1 = '''
    SELECT 
      substr(id, 1, 8) as id_prefix,
      count(*) as cnt,
      min(created_at) as first_created,
      max(created_at) as last_created
    FROM candidates
    WHERE id LIKE '32%' OR id LIKE '33%'
    GROUP BY substr(id, 1, 8)
    ORDER BY cnt DESC
    LIMIT 10
    '''
    rows1 = cur.execute(q1).fetchall()
    for r in rows1:
        print(f"Prefix: {r['id_prefix']} | Count: {r['cnt']} | Range: {r['first_created']} ~ {r['last_created']}")

    print('\n=== 2. Normal ID Timestamps ===')
    q2 = '''
    SELECT 
      min(created_at) as min_c,
      max(created_at) as max_c
    FROM candidates
    WHERE id NOT LIKE '32%' AND id NOT LIKE '33%'
    '''
    r2 = cur.execute(q2).fetchone()
    if r2:
        print(f"Normal Range: {r2['min_c']} ~ {r2['max_c']}")

    conn.close()

if __name__ == "__main__":
    analyze_timestamps()
