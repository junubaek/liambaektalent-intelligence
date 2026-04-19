import sqlite3
import bcrypt

salt = bcrypt.gensalt()
pw_hash = bcrypt.hashpw('qorwnsdn87'.encode('utf-8'), salt).decode('utf-8')

conn = sqlite3.connect('candidates.db')
cursor = conn.cursor()
cursor.execute("UPDATE users SET password_hash = ? WHERE id = 'liam'", (pw_hash,))
conn.commit()
conn.close()
print("Updated Liam password.")
