import sqlite3, sys
sys.stdout.reconfigure(encoding='utf-8')

def finalize_deletion_scope():
    conn = sqlite3.connect('candidates.db')
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    # 1. Safe to Delete: No contact info
    q1 = '''
    SELECT count(*) as safe_to_delete
    FROM candidates
    WHERE (id LIKE '32%' OR id LIKE '33%')
      AND (phone IS NULL OR phone = '')
      AND (email IS NULL OR email = '')
    '''
    res1 = cur.execute(q1).fetchone()
    print(f"Safe to Delete (No contact): {res1['safe_to_delete']}")

    # 2. Has Contact
    q2 = '''
    SELECT count(*) as has_contact
    FROM candidates  
    WHERE (id LIKE '32%' OR id LIKE '33%')
      AND (
           (phone IS NOT NULL AND phone != '')
           OR 
           (email IS NOT NULL AND email != '')
          )
    '''
    res2 = cur.execute(q2).fetchone()
    print(f"Has Contact: {res2['has_contact']}")

    # 3. Already in New (Overlap)
    q3 = '''
    SELECT count(*) as already_in_new
    FROM candidates a
    WHERE (a.id LIKE '32%' OR a.id LIKE '33%')
      AND (a.phone IS NOT NULL AND a.phone != '')
      AND EXISTS (
        SELECT 1 FROM candidates b
        WHERE b.name_kr = a.name_kr
          AND b.phone = a.phone
          AND b.id NOT LIKE '32%'
          AND b.id NOT LIKE '33%'
      )
    '''
    res3 = cur.execute(q3).fetchone()
    print(f"Already in New (Overlap): {res3['already_in_new']}")

    conn.close()

if __name__ == "__main__":
    finalize_deletion_scope()
