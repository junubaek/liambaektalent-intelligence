import sqlite3

def check_schema():
    conn = sqlite3.connect('candidates.db')
    cur = conn.cursor()
    cur.execute("PRAGMA table_info(candidates)")
    columns = [row[1] for row in cur.fetchall()]
    print("Columns:", columns)
    conn.close()

if __name__ == '__main__':
    check_schema()
