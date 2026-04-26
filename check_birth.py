import sqlite3

db_path = 'candidates.db'
conn = sqlite3.connect(db_path)
cur = conn.cursor()

# Get total candidates
cur.execute('SELECT count(*) FROM candidates')
total = cur.fetchone()[0]

# Get candidates with birth year (not null, not empty, and reasonably looking like a year)
# e.g., '1985', '90년생', etc. We'll just exclude NULL, empty, and "생년 미상" (Unknown)
cur.execute("SELECT count(*) FROM candidates WHERE birth_year IS NOT NULL AND birth_year != '' AND birth_year NOT LIKE '%생년%' AND birth_year NOT LIKE '%미상%'")
with_birth = cur.fetchone()[0]

# Let's also get a few examples of birth_year to see what format they are in
cur.execute("SELECT birth_year FROM candidates WHERE birth_year IS NOT NULL AND birth_year != '' AND birth_year NOT LIKE '%생년%' AND birth_year NOT LIKE '%미상%' LIMIT 5")
examples = [row[0] for row in cur.fetchall()]

print(f'Total Candidates: {total}')
print(f'With Birth Year: {with_birth}')
if total > 0:
    print(f'Percentage: {(with_birth / total) * 100:.2f}%')

print("Sample birth_year values:", examples)

conn.close()
