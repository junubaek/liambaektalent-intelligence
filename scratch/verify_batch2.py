import sqlite3

def final_verify_batch2():
    conn = sqlite3.connect('candidates.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    names = ['송경석', '방주용', '이우상', '류래민', '김태형']
    print("=== Final Verification Batch 2 ===")
    
    for name in names:
        print(f"\nChecking: {name}")
        rows = cursor.execute("SELECT id, name_kr, email, is_duplicate, duplicate_of FROM candidates WHERE name_kr = ?", (name,)).fetchall()
        for r in rows:
            print(f"  ID: {r['id']}, Name: {r['name_kr']}, Email: {r['email']}, Is_Dup: {r['is_duplicate']}, Dup_Of: {r['duplicate_of']}")
            
    # Search for any record that contains '김태형' in raw_text but is not labeled '김태형'
    print("\nSearching for '김태형' in raw_text (potential real record):")
    rows = cursor.execute("SELECT id, name_kr, email FROM candidates WHERE raw_text LIKE '%김태형%'").fetchall()
    for r in rows:
        print(f"  ID: {r['id']}, Name: {r['name_kr']}, Email: {r['email']}")

    conn.close()

if __name__ == "__main__":
    final_verify_batch2()
