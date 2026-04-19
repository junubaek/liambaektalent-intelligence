import os
import urllib.request

def ensure_db():
    db_path = os.environ.get('DB_PATH', 'candidates.db')
    
    # 이미 있으면 스킵
    if os.path.exists(db_path) and os.path.getsize(db_path) > 1000:
        print(f"DB 존재: {db_path} ({os.path.getsize(db_path)//1024//1024}MB)")
        return
    
    url = os.environ.get('DB_DOWNLOAD_URL', '')
    if not url:
        print("DB_DOWNLOAD_URL 없음. 로컬 DB 사용.")
        return
    
    print(f"DB 다운로드 중: {db_path}")
    if os.path.dirname(db_path):
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
    urllib.request.urlretrieve(url, db_path)
    print(f"DB 다운로드 완료: {os.path.getsize(db_path)//1024//1024}MB")

if __name__ == '__main__':
    ensure_db()
