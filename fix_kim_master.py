import sqlite3

conn = sqlite3.connect('candidates.db')
cur = conn.cursor()

# Set all Kim Eun-hyung records to duplicate
cur.execute("UPDATE candidates SET is_duplicate = 1 WHERE name_kr = '김은형'")

# Set the best one to master
best_id = "f5875fc2-99aa-4605-9742-5ec93f4cd51a"
cur.execute("UPDATE candidates SET is_duplicate = 0 WHERE id = ?", (best_id,))

conn.commit()
print(f"Master successfully updated to {best_id} for 김은형")
conn.close()
