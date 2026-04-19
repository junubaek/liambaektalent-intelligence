import sqlite3

def clear_last_error():
    conn = sqlite3.connect("candidates.db")
    cursor = conn.cursor()
    cursor.execute("UPDATE candidates SET last_error = NULL WHERE last_error IS NOT NULL")
    count = cursor.rowcount
    conn.commit()
    conn.close()
    print(f"Cleared last_error for {count} candidates.")

if __name__ == "__main__":
    clear_last_error()
