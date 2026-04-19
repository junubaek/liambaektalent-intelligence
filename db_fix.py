import sqlite3
conn = sqlite3.connect('candidates.db')
cursor = conn.cursor()
cursor.execute("DELETE FROM users WHERE id = 'userB'")
cursor.execute("UPDATE users SET name = 'Liam' WHERE id = 'liam'")
conn.commit()
conn.close()
print('DB updated.')
