import sqlite3

def find_by_name(name):
    conn = sqlite3.connect('candidates.db')
    cursor = conn.cursor()
    cursor.execute("SELECT id, name_kr FROM candidates WHERE name_kr LIKE ?", (f"%{name}%",))
    rows = cursor.fetchall()
    print(f"Searching for '{name}':")
    for row in rows:
        print(f"ID: {row[0]}, Name: {row[1]}")
    conn.close()

if __name__ == "__main__":
    find_by_name("박지연")
    find_by_name("박소이")
    find_by_name("최수미")
