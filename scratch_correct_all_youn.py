import sqlite3
import subprocess

db_path = "candidates.db"
conn = sqlite3.connect(db_path)
cur = conn.cursor()

# Set all 이영도 records to Product sector
cur.execute("UPDATE candidates SET sector = 'Product' WHERE name_kr = '이영도'")
conn.commit()
print("Successfully set all 이영도 records to 'Product' sector in candidates.db!")
conn.close()

# Rebuild indices
print("Rebuilding index caches...")
subprocess.run("python build_ontology_vector.py", shell=True)
subprocess.run("python build_bm25_index.py", shell=True)
print("Rebuild finished successfully!")
