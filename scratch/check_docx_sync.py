import sqlite3

def check():
    conn = sqlite3.connect('candidates.db')
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM candidates WHERE source_file LIKE '%.docx' AND is_neo4j_synced = 1")
    synced = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM candidates WHERE source_file LIKE '%.docx' AND (is_neo4j_synced = 0 OR is_neo4j_synced IS NULL)")
    not_synced = cursor.fetchone()[0]
    
    print(f"Synced .docx: {synced}")
    print(f"Not synced .docx: {not_synced}")
    conn.close()

if __name__ == "__main__":
    check()
