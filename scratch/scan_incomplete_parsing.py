import sqlite3
import json

def scan_incomplete_parsing():
    conn = sqlite3.connect('candidates.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    report = {
        'never_parsed': [],
        'missing_career': [],
        'missing_education': [],
        'missing_company_sector': []
    }
    
    # 1. Never parsed
    cursor.execute("SELECT id, name_kr, email FROM candidates WHERE is_parsed = 0")
    report['never_parsed'] = [dict(r) for r in cursor.fetchall()]
    
    # 2. Parsed but no career info
    cursor.execute("SELECT id, name_kr, email FROM candidates WHERE is_parsed = 1 AND (careers_json IS NULL OR careers_json = '[]' OR careers_json = '')")
    report['missing_career'] = [dict(r) for r in cursor.fetchall()]
    
    # 3. Parsed but no education info
    cursor.execute("SELECT id, name_kr, email FROM candidates WHERE is_parsed = 1 AND (education_json IS NULL OR education_json = '[]' OR education_json = '')")
    report['missing_education'] = [dict(r) for r in cursor.fetchall()]
    
    # 4. Missing current company or sector
    cursor.execute("SELECT id, name_kr, email FROM candidates WHERE is_parsed = 1 AND (current_company IS NULL OR current_company = '' OR sector IS NULL OR sector = '')")
    report['missing_company_sector'] = [dict(r) for r in cursor.fetchall()]
    
    # Summary
    print(f"Never Parsed: {len(report['never_parsed'])}")
    print(f"Missing Career: {len(report['missing_career'])}")
    print(f"Missing Education: {len(report['missing_education'])}")
    print(f"Missing Co/Sector: {len(report['missing_company_sector'])}")
    
    with open('incomplete_parsing_report.json', 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
        
    conn.close()

if __name__ == "__main__":
    scan_incomplete_parsing()
