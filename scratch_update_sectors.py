import sqlite3

db_path = "candidates.db"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

updates = [
    ("Eng_Semi", "양민철", "767f5579-5955-4263-ab9c-f1fb494585b5"),
    ("Eng_Semi", "이민영", "f68c8639-4656-4e6c-a986-8fcdaf76c22e"),
    ("Product", "안유리", "79d1edd5-7001-4f71-bc2b-95de15b11101"),
    ("Eng_Data", "정혜연", "07043d62-db55-458e-a43e-2243d30f4065"),
    ("Eng_Data", "김태익", "c2d2ff7d-0099-43b0-9e57-40fac1a2fa9e"),
    ("Strategy", "강성주", "1e73a38a-9c39-414e-b95d-3e522183ed27"),
    ("Product", "백재현", "dd8f311c-ce27-4e91-a739-5ec68024ab21")
]

print("--- Before Update ---")
for sector, name, cid in updates:
    cursor.execute("SELECT id, name_kr, sector FROM candidates WHERE id = ?", (cid,))
    row = cursor.fetchone()
    print(f"ID: {cid}, Name: {name}, Current Row: {row}")

print("\n--- Updating ---")
for sector, name, cid in updates:
    cursor.execute("UPDATE candidates SET sector = ? WHERE name_kr = ? AND id = ?", (sector, name, cid))
    print(f"Updated {name} ({cid}) to {sector}. Rows affected: {cursor.rowcount}")

conn.commit()

print("\n--- After Update ---")
for sector, name, cid in updates:
    cursor.execute("SELECT id, name_kr, sector FROM candidates WHERE id = ?", (cid,))
    row = cursor.fetchone()
    print(f"ID: {cid}, Name: {name}, Updated Row: {row}")

conn.close()
