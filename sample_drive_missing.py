import sqlite3
import json
from sqlalchemy import text
from app.database import SessionLocal
from connectors.notion_api import HeadhunterDB

def main():
    db = SessionLocal()
    notion = HeadhunterDB()

    q = """
    SELECT id, name_kr 
    FROM candidates 
    WHERE is_duplicate=0 
    AND (google_drive_url IS NULL OR google_drive_url = '' OR google_drive_url = '#')
    LIMIT 100
    """
    
    targets = db.execute(text(q)).fetchall()
    
    case_a_count = 0
    case_b_count = 0
    case_c_count = 0
    
    s3_url_samples = []

    for cid, name in targets:
        # Check Notion page properties and potentially blocks if needed.
        page_data = notion.client._request("GET", f"pages/{cid}")
        
        if not page_data or 'error' in page_data or page_data.get('object') == 'error':
            case_c_count += 1
            continue
            
        props = page_data.get("properties", {})
        
        # Check for files / s3 links
        has_file = False
        for prop_name, prop_data in props.items():
            if prop_data.get("type") == "files":
                files_list = prop_data.get("files", [])
                if files_list:
                    has_file = True
                    for f in files_list:
                        # Notion hosted files have type "file"
                        f_type = f.get("type", "")
                        if f_type == "file":
                            s3_url = f.get("file", {}).get("url", "")
                            if s3_url and len(s3_url_samples) < 3:
                                s3_url_samples.append(s3_url)
                        elif f_type == "external":
                            # It's an external URL but not drive since we filtered drive out previously
                            ext_url = f.get("external", {}).get("url", "")
                            if ext_url and "drive" not in ext_url and len(s3_url_samples) < 3:
                                s3_url_samples.append(ext_url)
                    break
        
        if has_file:
            case_a_count += 1
        else:
            case_b_count += 1
            
    print("=== 결과 ===")
    print(f"샘플 크기: {len(targets)}명")
    print(f"케이스 A (S3 첨부): {case_a_count}명 ({case_a_count}% 예상)")
    print(f"케이스 B (텍스트만): {case_b_count}명 ({case_b_count}% 예상)")
    print(f"케이스 C (404/접근불가): {case_c_count}명 ({case_c_count}% 예상)")
    
    print("\n[Case A - S3 URL 형식 샘플]")
    for s in s3_url_samples:
        # url might be long, slice to show format
        print(s[:100] + "...")

if __name__ == "__main__":
    main()
