import sqlite3

def analyze_jung():
    conn = sqlite3.connect('candidates.db')
    conn.row_factory = sqlite3.Row
    cid = '32122567-1b6f-8124-b68d-e58d82237481'
    row = conn.cursor().execute('SELECT raw_text FROM candidates WHERE id = ?', (cid,)).fetchone()
    if row:
        raw_text = row['raw_text']
        # Try to find phone pattern like 010-XXXX-XXXX
        import re
        phones = re.findall(r'010-\d{3,4}-\d{4}', raw_text)
        emails = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', raw_text)
        print(f"Found phones: {phones}")
        print(f"Found emails: {emails}")
        # Print first 2000 chars safely
        print("Raw text snippet:")
        print(raw_text[:2000].encode('ascii', 'replace').decode('ascii'))
    conn.close()

if __name__ == "__main__":
    analyze_jung()
