import sqlite3

def upgrade_schema():
    conn = sqlite3.connect('candidates.db')
    cur = conn.cursor()
    
    # Check existing columns to avoid errors if run twice
    cur.execute("PRAGMA table_info(candidates)")
    columns = [col[1] for col in cur.fetchall()]
    
    if 'cei_json' not in columns:
        cur.execute("ALTER TABLE candidates ADD COLUMN cei_json TEXT;")
        print("Added cei_json")
    if 'cei_confidence' not in columns:
        cur.execute("ALTER TABLE candidates ADD COLUMN cei_confidence REAL DEFAULT 0.0;")
        print("Added cei_confidence")
    if 'cei_updated_at' not in columns:
        cur.execute("ALTER TABLE candidates ADD COLUMN cei_updated_at TEXT;")
        print("Added cei_updated_at")
        
    conn.commit()
    conn.close()

if __name__ == '__main__':
    upgrade_schema()
