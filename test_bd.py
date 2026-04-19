import sqlite3

def main():
    conn = sqlite3.connect('C:/Users/cazam/Downloads/이력서자동분석검색시스템/candidates.db')
    c = conn.cursor()
    c.execute("""
    SELECT count(*) FROM candidates
    WHERE raw_text LIKE '%사업개발%'
       OR raw_text LIKE '%신사업%'
       OR raw_text LIKE '%파트너십%'
       OR raw_text LIKE '%Business Development%'
       OR raw_text LIKE '% BD %'
    """)
    count = c.fetchone()[0]
    print(f"BD Count: {count}")
    conn.close()

if __name__ == '__main__':
    main()
