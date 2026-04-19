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
    
    case_a_count = 0 # S3 file
    case_b_count = 0 # Text/other blocks
    case_c_count = 0 # 404
    case_empty = 0   # Completely empty blocks
    
    s3_url_samples = []

    for i, (cid, name) in enumerate(targets):
        blocks_data = notion.client._request("GET", f"blocks/{cid}/children")
        
        if not blocks_data or 'error' in blocks_data or blocks_data.get('object') == 'error':
            case_c_count += 1
            time.sleep(0.3)
            continue
            
        blocks = blocks_data.get("results", [])
        
        if not blocks:
            case_empty += 1
            time.sleep(0.3)
            continue

        has_file = False
        for b in blocks:
            btype = b.get("type", "")
            if btype in ("file", "pdf"):
                has_file = True
                file_obj = b.get(btype, {})
                s3_url = ""
                if file_obj.get("type") == "file":
                    s3_url = file_obj.get("file", {}).get("url", "")
                elif file_obj.get("type") == "external":
                    s3_url = file_obj.get("external", {}).get("url", "")
                
                if s3_url and len(s3_url_samples) < 3:
                    s3_url_samples.append(s3_url)
                
        if has_file:
            case_a_count += 1
        else:
            case_b_count += 1
            
        time.sleep(0.3)
            
    print("=== 결과 ===")
    print(f"샘플 크기: {len(targets)}명")
    print(f"케이스 A (S3 첨부 등 파일블록 보유): {case_a_count}명 ({case_a_count}% 예상)")
    print(f"케이스 B (기타 텍스트/이미지 등 블록 보유): {case_b_count}명 ({case_b_count}% 예상)")
    print(f"케이스 EMPTY (블록이 전혀 없는 빈 페이지): {case_empty}명 ({case_empty}% 예상)")
    print(f"케이스 C (404/접근불가): {case_c_count}명 ({case_c_count}% 예상)")
    
    print("\n[Case A - S3 URL 형식 샘플]")
    for s in s3_url_samples:
        print(s[:150] + "...")

if __name__ == "__main__":
    main()
