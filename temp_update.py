import sqlite3

def run():
    conn = sqlite3.connect('candidates.db')
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE candidates
        SET is_neo4j_synced = 1
        WHERE is_neo4j_synced = 0
    """)
    print(f"Rows updated for is_neo4j_synced: {cursor.rowcount}")
    conn.commit()

if __name__ == '__main__':
    run()
