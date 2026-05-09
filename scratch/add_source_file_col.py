import sqlite3

def add_column():
    conn = sqlite3.connect('candidates.db')
    cursor = conn.cursor()
    try:
        cursor.execute("ALTER TABLE candidates ADD COLUMN source_file TEXT")
        print("Added source_file column.")
    except sqlite3.OperationalError as e:
        print(f"Column check: {e}")
    conn.commit()
    conn.close()

if __name__ == "__main__":
    add_column()
