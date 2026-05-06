import sqlite3
import re
import json

def scan_for_issues():
    conn = sqlite3.connect('candidates.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    issues = []
    
    # 1. Scan for garbled names
    print("Scanning for garbled names...")
    cursor.execute("SELECT id, name_kr, email FROM candidates WHERE name_kr LIKE '%%' OR name_kr IS NULL OR name_kr = ''")
    rows = cursor.fetchall()
    for row in rows:
        issues.append({
            'type': 'Garbled/Missing Name',
            'id': row['id'],
            'current_name': row['name_kr'],
            'email': row['email'],
            'reason': 'Contains replacement character or is empty'
        })
        
    # 2. Scan for potential duplicates by Email
    print("Scanning for duplicates by Email...")
    cursor.execute("""
        SELECT email, COUNT(*) as count 
        FROM candidates 
        WHERE email IS NOT NULL AND email != '' AND is_duplicate = 0
        GROUP BY email 
        HAVING count > 1
    """)
    dup_emails = cursor.fetchall()
    for d in dup_emails:
        cursor.execute("SELECT id, name_kr FROM candidates WHERE email = ? AND is_duplicate = 0", (d['email'],))
        dup_rows = cursor.fetchall()
        issues.append({
            'type': 'Potential Duplicate (Email)',
            'email': d['email'],
            'count': d['count'],
            'records': [{'id': r['id'], 'name': r['name_kr']} for r in dup_rows]
        })
        
    # 3. Scan for potential name mismatches
    # We look for names in name_kr that don't appear in the first 1000 chars of raw_text,
    # OR cases where a different name appears prominently.
    # This is harder, so we'll focus on common patterns.
    print("Scanning for name mismatches (this may take a while)...")
    cursor.execute("SELECT id, name_kr, raw_text FROM candidates WHERE is_duplicate = 0 AND name_kr IS NOT NULL AND name_kr != '' LIMIT 500")
    rows = cursor.fetchall()
    for row in rows:
        name = row['name_kr']
        text = row['raw_text'] if row['raw_text'] else ""
        if len(name) >= 2 and name not in text:
            # Check if there's another name pattern like '성명 : XXX' or '이 름 : XXX'
            match = re.search(r'(?:성명|이\s*름)\s*[:：]\s*([가-힣]{2,4})', text)
            if match:
                extracted_name = match.group(1)
                if extracted_name != name:
                    issues.append({
                        'type': 'Name Mismatch',
                        'id': row['id'],
                        'db_name': name,
                        'text_name': extracted_name,
                        'reason': f"DB name '{name}' not found in text, but '{extracted_name}' found after label."
                    })

    # Output results to a file for the user
    with open('data_issues_report.json', 'w', encoding='utf-8') as f:
        json.dump(issues, f, ensure_ascii=False, indent=2)
        
    print(f"Scan complete. Found {len(issues)} potential issues.")
    return issues

if __name__ == "__main__":
    scan_for_issues()
