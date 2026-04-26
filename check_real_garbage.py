import sqlite3, sys
sys.stdout.reconfigure(encoding='utf-8')

def check_real_garbage():
    conn = sqlite3.connect('candidates.db')
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    q = '''
    SELECT count(*) as real_garbage
    FROM candidates
    WHERE (id LIKE '32%' OR id LIKE '33%')
      AND (
        name_kr IS NULL 
        OR name_kr = ''
        OR name_kr = 'None'
        OR length(name_kr) < 2
      )
      AND (profile_summary IS NULL OR profile_summary = '')
    '''
    res = cur.execute(q).fetchone()
    print(f"Real Garbage count: {res['real_garbage']}")

    conn.close()

if __name__ == "__main__":
    check_real_garbage()
