import sqlite3
conn = sqlite3.connect('candidates.db')
cur = conn.cursor()

# Set bad record to duplicate
cur.execute("UPDATE candidates SET is_duplicate = 1 WHERE id = '33522567-1b6f-81a3-ac63-e62ab98e6793'")

# Set good record to active
cur.execute("UPDATE candidates SET is_duplicate = 0 WHERE id = '95207af2-552f-43ad-afcb-4d883fbacbb6'")

conn.commit()
conn.close()
print('Swapped duplicate status')
