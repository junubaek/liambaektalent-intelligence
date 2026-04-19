import time
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
    
    case_a_count = 0 # S3 file inside properties or blocks
    case_b_count = 0 # Text only
    case_c_count = 0 # 404
    case_empty = 0
    
    s3_url_samples = []

    for i, (cid, name) in enumerate(targets):
        page_data = notion.client._request("GET", f"pages/{cid}")
        
        if not page_data or 'error' in page_data or page_data.get('object') == 'error':
            case_c_count += 1
            time.sleep(0.3)
            continue
            
        props = page_data.get("properties", {})
        has_file_in_prop = False
        
        # Check properties for files (S3 attachments)
        for prop_name, prop_data in props.items():
            if prop_data.get("type") == "files":
                files_list = prop_data.get("files", [])
                if files_list:
                    for f in files_list:
                        # Internal Notion upload uses 'file' type (S3 backend)
                        if f.get("type") == "file":
                            s3_url = f.get("file", {}).get("url", "")
                            if s3_url:
                                has_file_in_prop = True
                                if len(s3_url_samples) < 3:
                                    s3_url_samples.append(s3_url)
                        # External also checked just in case
                        elif f.get("type") == "external":
                            url = f.get("external", {}).get("url", "")
                            if url and "drive.google" not in url:
                                has_file_in_prop = True
                                if len(s3_url_samples) < 3:
                                    s3_url_samples.append(url)
                                    
        if has_file_in_prop:
            case_a_count += 1
            time.sleep(0.3)
            continue
            
        # If no files in properties, check blocks
        blocks_data = notion.client._request("GET", f"blocks/{cid}/children")
        blocks = blocks_data.get("results", []) if blocks_data else []
        
        if not blocks:
            # No files in props + no blocks = completely empty body
            case_empty += 1
            time.sleep(0.3)
            continue

        has_file_in_block = False
        for b in blocks:
            btype = b.get("type", "")
            if btype in ("file", "pdf"):
                has_file_in_block = True
                file_obj = b.get(btype, {})
                s3_url = ""
                if file_obj.get("type") == "file":
                    s3_url = file_obj.get("file", {}).get("url", "")
                
                if s3_url and len(s3_url_samples) < 3:
                    s3_url_samples.append(s3_url)
                
        if has_file_in_block:
            case_a_count += 1
        else:
            case_b_count += 1
            
        time.sleep(0.3)
            
    print("=== 결과 ===")
    print(f"샘플 크기: {len(targets)}명")
    print(f"케이스 A (S3 첨부 파일 보유): {case_a_count}명 ({case_a_count}% 예상)")
    print(f"케이스 B (텍스트/이미지만 있고 첨부파일 없음): {case_b_count}명 ({case_b_count}% 예상)")
    print(f"케이스 EMPTY (첨부파일 없고 본문도 빈 페이지): {case_empty}명 ({case_empty}% 예상)")
    print(f"케이스 C (404/접근불가): {case_c_count}명 ({case_c_count}% 예상)")
    
    print("\n[Case A - S3 URL 형식 샘플]")
    for s in s3_url_samples:
        print(s[:120] + "...")

if __name__ == "__main__":
    main()
