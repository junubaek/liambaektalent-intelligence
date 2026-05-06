import sqlite3

def final_verification():
    conn = sqlite3.connect('candidates.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    print("=== Final Verification ===")
    
    # 1. Check Names
    names = ['백민종', '정진숙', '배정석']
    for name in names:
        print(f"\nChecking: {name}")
        rows = cursor.execute("SELECT id, name_kr, email, current_company, is_duplicate, duplicate_of FROM candidates WHERE name_kr = ?", (name,)).fetchall()
        if not rows:
            print("No record found with this exact name!")
        for r in rows:
            print(f"  ID: {r['id']}")
            print(f"  Name: {r['name_kr']}")
            print(f"  Email: {r['email']}")
            print(f"  Company: {r['current_company']}")
            print(f"  Is_Dup: {r['is_duplicate']}")
            print(f"  Dup_Of: {r['duplicate_of']}")
            
    # 2. Search for missed duplicates by email/phone
    print("\n=== Searching for missed duplicates by Email ===")
    emails = ['bmjzz123@naver.com', 'jeongseoke@gmail.com']
    for email in emails:
        print(f"\nEmail: {email}")
        rows = cursor.execute("SELECT id, name_kr, is_duplicate, duplicate_of FROM candidates WHERE email = ?", (email,)).fetchall()
        for r in rows:
            print(f"  ID: {r['id']}, Name: {r['name_kr']}, Is_Dup: {r['is_duplicate']}, Dup_Of: {r['duplicate_of']}")

    conn.close()

if __name__ == "__main__":
    final_verification()
