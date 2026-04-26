import sqlite3, sys
sys.stdout.reconfigure(encoding='utf-8')

def final_overlap_check():
    conn = sqlite3.connect('candidates.db')
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    print('=== 1. Overlap Check (Old vs New) ===')
    q1 = '''
    SELECT 
      a.name_kr,
      a.phone,
      a.id as old_id,
      b.id as new_id
    FROM candidates a
    JOIN candidates b 
      ON a.name_kr = b.name_kr 
      AND a.phone = b.phone
      AND a.phone IS NOT NULL
    WHERE (a.id LIKE '32%' OR a.id LIKE '33%')
      AND b.id NOT LIKE '32%' 
      AND b.id NOT LIKE '33%'
    LIMIT 10
    '''
    rows1 = cur.execute(q1).fetchall()
    if rows1:
        for r in rows1:
            print(f"Name: {r['name_kr']} | Phone: {r['phone']} | Old: {r['old_id'][:8]} | New: {r['new_id'][:8]}")
    else:
        print("No overlaps found based on Name & Phone.")

    print('\n=== 2. Unique Old Candidates count ===')
    q2 = '''
    SELECT count(*) as unique_old
    FROM candidates a
    WHERE (a.id LIKE '32%' OR a.id LIKE '33%')
      AND NOT EXISTS (
        SELECT 1 FROM candidates b
        WHERE b.name_kr = a.name_kr
          AND b.phone = a.phone
          AND b.phone IS NOT NULL
          AND b.id NOT LIKE '32%'
          AND b.id NOT LIKE '33%'
      )
    '''
    r2 = cur.execute(q2).fetchone()
    if r2:
        print(f"Unique Old Candidates: {r2['unique_old']}")

    conn.close()

if __name__ == "__main__":
    final_overlap_check()
