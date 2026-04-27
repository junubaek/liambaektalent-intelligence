import os
import urllib.request

def ensure_db():
    db_path = os.environ.get('DB_PATH', 'candidates.db')
    
    # Check if DB exists and has the 'candidates' table with data
    if os.path.exists(db_path) and os.path.getsize(db_path) > 1000:
        try:
            import sqlite3
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            # Stricter check: try to count rows in candidates table
            cursor.execute("SELECT COUNT(*) FROM candidates;")
            count = cursor.fetchone()[0]
            conn.close()
            
            if count > 0:
                print(f"DB 존재 및 검증 완료: {db_path} ({os.path.getsize(db_path)//1024//1024}MB, {count}명)")
                return
            else:
                print(f"DB에 데이터가 없음 (0명). 재다운로드 진행: {db_path}")
                os.remove(db_path)
        except Exception as e:
            print(f"DB 검증 실패 (테이블 누락 또는 손상): {e}")
            if os.path.exists(db_path):
                try:
                    conn.close() # Ensure connection is closed before deletion
                except: pass
                os.remove(db_path)
    
    url = os.environ.get('DB_DOWNLOAD_URL', '')
    if not url:
        print("DB_DOWNLOAD_URL 없음. 로컬 DB 사용.")
        return
    
    print(f"DB 다운로드 중: {db_path}")
    if os.path.dirname(db_path):
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
    
    try:
        import urllib.request
        urllib.request.urlretrieve(url, db_path)
        print(f"DB 다운로드 완료: {os.path.getsize(db_path)//1024//1024}MB")
    except Exception as e:
        print(f"DB 다운로드 실패: {e}")



if __name__ == '__main__':
    ensure_db()
