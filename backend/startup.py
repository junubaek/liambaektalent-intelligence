import os
import urllib.request

def ensure_db():
    db_path = os.environ.get('DB_PATH', 'candidates.db')
    
    # Check if DB exists and has the 'candidates' table
    if os.path.exists(db_path) and os.path.getsize(db_path) > 1000:
        try:
            import sqlite3
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='candidates';")
            table_exists = cursor.fetchone()
            conn.close()
            if table_exists:
                print(f"DB 존재 및 검증 완료: {db_path} ({os.path.getsize(db_path)//1024//1024}MB)")
                return
            else:
                print(f"DB 파일은 존재하나 'candidates' 테이블이 없음. 재설정 진행: {db_path}")
                os.remove(db_path)
        except Exception as e:
            print(f"DB 검증 중 오류 발생, 재다운로드 시도: {e}")
            if os.path.exists(db_path):
                os.remove(db_path)
    
    url = os.environ.get('DB_DOWNLOAD_URL', '')
    if not url:
        print("DB_DOWNLOAD_URL 없음. 로컬 DB 사용.")
        return
    
    print(f"DB 다운로드 중: {db_path}")
    if os.path.dirname(db_path):
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
    
    try:
        urllib.request.urlretrieve(url, db_path)
        print(f"DB 다운로드 완료: {os.path.getsize(db_path)//1024//1024}MB")
    except Exception as e:
        print(f"DB 다운로드 실패: {e}")


if __name__ == '__main__':
    ensure_db()
