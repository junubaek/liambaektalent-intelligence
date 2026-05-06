import sqlite3
import bcrypt

DB_PATH = "candidates.db"

def test_login(user_id, password):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    user = conn.cursor().execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
    conn.close()
    
    if not user:
        print(f"User {user_id} not found.")
        return False
    
    if bcrypt.checkpw(password.encode('utf-8'), user['password_hash'].encode('utf-8')):
        print(f"Login successful for {user_id}!")
        return True
    else:
        print(f"Login failed for {user_id}. Password mismatch.")
        return False

if __name__ == "__main__":
    test_login("liam", "qorwnsdn87")
