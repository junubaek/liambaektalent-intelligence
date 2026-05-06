import sqlite3

DB_PATH = "candidates.db"

def check_users():
    if not os.path.exists(DB_PATH):
        print(f"Error: {DB_PATH} not found.")
        return

    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Check if users table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users';")
        if not cursor.fetchone():
            print("Table 'users' does not exist.")
            return

        cursor.execute("SELECT id, name, role, is_admin FROM users")
        users = cursor.fetchall()
        print(f"Users found: {len(users)}")
        for u in users:
            print(u)
        
        conn.close()
    except Exception as e:
        print(f"Error checking users: {e}")

import os
if __name__ == "__main__":
    check_users()
