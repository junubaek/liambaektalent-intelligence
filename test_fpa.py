import sqlite3

def main():
    conn = sqlite3.connect('C:/Users/cazam/Downloads/이력서자동분석검색시스템/candidates.db')
    c = conn.cursor()
    c.execute("""
    SELECT count(*) FROM candidates
    WHERE raw_text LIKE '%FP&A%'
       OR raw_text LIKE '%FP%A%'
       OR raw_text LIKE '%재무기획%'
       OR raw_text LIKE '%예산기획%'
    """)
    count = c.fetchone()[0]
    print(f"FP&A Count: {count}")
    conn.close()

if __name__ == '__main__':
    main()
