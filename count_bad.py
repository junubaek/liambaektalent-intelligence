import sqlite3

def count_bad_names():
    conn = sqlite3.connect('candidates.db')
    cur = conn.cursor()
    cur.execute("SELECT count(*) FROM candidates WHERE name_kr LIKE '%(%' OR name_kr LIKE '%미상%' OR name_kr LIKE 'null%' OR name_kr='이름' OR name_kr='UX컨설팅'")
    print(cur.fetchone()[0])
    conn.close()

if __name__ == '__main__':
    count_bad_names()
