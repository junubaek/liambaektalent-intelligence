import sqlite3

def fix_all_requested():
    conn = sqlite3.connect('candidates.db')
    cursor = conn.cursor()
    
    # 1. 송경석 (Song Gyeong-seok)
    print("Updating 송경석...")
    cursor.execute("UPDATE candidates SET name_kr = ?, is_duplicate = 0 WHERE id = ?", ('송경석', '8b8d60cc-dfed-4a5b-a15f-57e7aae84b91'))
    cursor.execute("UPDATE candidates SET is_duplicate = 1, duplicate_of = ? WHERE id = ?", ('8b8d60cc-dfed-4a5b-a15f-57e7aae84b91', '32e22567-1b6f-8133-9343-f16e8932d3a5'))
    
    # 2. 방주용 (Bang Ju-yong)
    print("Updating 방주용...")
    cursor.execute("UPDATE candidates SET name_kr = ?, current_company = ?, is_duplicate = 0 WHERE id = ?", ('방주용', '한화', '1292808e-4c89-4738-adf4-f2b03ee76a98'))
    cursor.execute("UPDATE candidates SET is_duplicate = 1, duplicate_of = ? WHERE id = ?", ('1292808e-4c89-4738-adf4-f2b03ee76a98', '33522567-1b6f-8103-9468-e9ce12fdefc9'))
    
    # 3. 이우상 (Lee Woo-sang)
    print("Updating 이우상...")
    cursor.execute("UPDATE candidates SET name_kr = ? WHERE id = ?", ('이우상', '32122567-1b6f-8164-86ab-f547693c6de9'))
    
    # 4. 김태형 vs 류래민 (Mismatch Fix)
    # The record 32022567-1b6f-8196-b5de-ef936a5c5e66 is mislabeled as 김태형 but is actually 류래민
    # The correct 류래민 record is 532ff520-679c-4d7f-b8e4-7e16467b3f18
    print("Fixing 김태형 vs 류래민 mismatch...")
    # First, make sure 532ff520-679c-4d7f-b8e4-7e16467b3f18 is labeled as 류래민
    cursor.execute("UPDATE candidates SET name_kr = ? WHERE id = ?", ('류래민', '532ff520-679c-4d7f-b8e4-7e16467b3f18'))
    # Then merge the mislabeled record into it
    cursor.execute("UPDATE candidates SET is_duplicate = 1, duplicate_of = ?, name_kr = ? WHERE id = ?", ('532ff520-679c-4d7f-b8e4-7e16467b3f18', '류래민', '32022567-1b6f-8196-b5de-ef936a5c5e66'))
    
    conn.commit()
    print("All updates committed.")
    
    conn.close()

if __name__ == "__main__":
    fix_all_requested()
