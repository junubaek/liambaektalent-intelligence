import sqlite3

def fix_candidates():
    conn = sqlite3.connect('candidates.db')
    cursor = conn.cursor()
    
    # 1. Fix 백민종 (Baek Min-jong)
    print("Updating 백민종...")
    cursor.execute("UPDATE candidates SET name_kr = ?, current_company = ?, is_duplicate = 0 WHERE id = ?", ('백민종', '한화', '535fa3b5-dd87-486d-8023-687308450f05'))
    cursor.execute("UPDATE candidates SET is_duplicate = 1, duplicate_of = ? WHERE id = ?", ('535fa3b5-dd87-486d-8023-687308450f05', '33522567-1b6f-81e4-8b23-f31b4bd5d1de'))
    
    # 2. Fix 정진숙 (Jung Jin-sook)
    print("Updating 정진숙...")
    cursor.execute("UPDATE candidates SET name_kr = ? WHERE id = ?", ('정진숙', '32122567-1b6f-8124-b68d-e58d82237481'))
    
    # 3. Fix 배정석 (Bae Jeong-seok)
    print("Updating 배정석...")
    cursor.execute("UPDATE candidates SET name_kr = ?, current_company = ?, is_duplicate = 0 WHERE id = ?", ('배정석', '현대모비스', '530e31e5-30ff-4c43-8dc6-e31ca5ceeecd'))
    cursor.execute("UPDATE candidates SET is_duplicate = 1, duplicate_of = ? WHERE id = ?", ('530e31e5-30ff-4c43-8dc6-e31ca5ceeecd', '33522567-1b6f-8143-90e5-cbc0bf53044b'))
    
    conn.commit()
    print("Updates committed.")
    
    # Final check
    print("\nVerification:")
    names = ['백민종', '정진숙', '배정석']
    for name in names:
        rows = cursor.execute("SELECT id, name_kr, is_duplicate, duplicate_of FROM candidates WHERE name_kr = ?", (name,)).fetchall()
        for r in rows:
            print(f"Name: {r[1]}, ID: {r[0]}, Is_Dup: {r[2]}, Dup_Of: {r[3]}")
            
    conn.close()

if __name__ == "__main__":
    fix_candidates()
