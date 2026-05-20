import os
import urllib.request
import sys

# 로그 즉시 출력
sys.stdout.reconfigure(line_buffering=True)

# Add root directory to sys.path to allow importing modules from root
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

def ensure_db():
    print("=== ensure_db() 시작 ===", flush=True)
    import os
    db_path = os.environ.get('DB_PATH', 'candidates.db')
    
    db_dir = os.path.dirname(db_path) if os.path.dirname(db_path) else '.'
    url_version_file = os.path.join(db_dir, 'last_download_url.txt')
    
    url = os.environ.get('DB_DOWNLOAD_URL', '')
    # 구 ID이거나 URL이 비어 있는 경우 새 ID로 강제 오버라이드
    if '1oQ-Oa0OZJaBFiNin-GdZLOQfQalkOfDY' in url or not url:
        url = 'https://drive.google.com/uc?export=download&id=1dHOIZg_-EvsUNmvVFycrtNNfcuCbfhyj'
        print(f"DB_DOWNLOAD_URL 오버라이드 적용: {url}")
    
    # FORCE_DB_REDOWNLOAD 체크
    force_redownload = os.environ.get('FORCE_DB_REDOWNLOAD', 'false').lower() == 'true'
    
    last_url = ''
    if os.path.exists(url_version_file):
        try:
            with open(url_version_file, 'r', encoding='utf-8') as f:
                last_url = f.read().strip()
        except Exception as e:
            print(f"URL 버전 파일 읽기 실패: {e}")

    # 다운로드할 대상 URL이 기존에 받았던 URL과 다르면 기존 DB 삭제해서 재다운로드 강제
    if last_url != url:
        print(f"새로운 DB_DOWNLOAD_URL 감지 ({last_url} -> {url}). 기존 DB가 있을 경우 삭제 처리합니다.")
        if os.path.exists(db_path):
            try:
                os.remove(db_path)
                print("이전 DB 파일 삭제 완료.")
            except Exception as e:
                print(f"이전 DB 파일 삭제 실패: {e}")
    
    if force_redownload and os.path.exists(db_path):
        try:
            os.remove(db_path)
            print("FORCE_DB_REDOWNLOAD: 기존 DB 삭제 완료. 재다운로드 시작...")
        except Exception as e:
            print(f"FORCE_DB_REDOWNLOAD 삭제 실패: {e}")
    
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
    
    if not url:
        print("DB_DOWNLOAD_URL 없음. 로컬 DB 사용.")
        return
    
    print(f"DB 다운로드 중: {db_path}")
    if os.path.dirname(db_path):
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
    
    try:
        import requests
        import urllib.parse
        
        parsed = urllib.parse.urlparse(url)
        params = urllib.parse.parse_qs(parsed.query)
        file_id = params.get('id', [None])[0]
        
        if not file_id:
            # Fallback to direct urlretrieve if no ID can be parsed
            import urllib.request
            urllib.request.urlretrieve(url, db_path)
        else:
            base_url = "https://drive.google.com/uc?export=download"
            session = requests.Session()
            response = session.get(base_url, params={"id": file_id}, stream=True)
            
            token = None
            for key, value in response.cookies.items():
                if key.startswith("download_warning"):
                    token = value
                    break
            
            if token:
                response = session.get(base_url, params={"id": file_id, "confirm": token}, stream=True)
            
            with open(db_path, "wb") as f:
                for chunk in response.iter_content(32768):
                    if chunk:
                        f.write(chunk)
 
        print(f"DB 다운로드 완료: {os.path.getsize(db_path)//1024//1024}MB")
        
        # 다운로드 완료 후 버전 정보 파일 기록
        try:
            with open(url_version_file, 'w', encoding='utf-8') as f:
                f.write(url)
            print(f"URL 버전 파일 갱신 완료: {url}")
        except Exception as e:
            print(f"URL 버전 파일 기록 실패: {e}")

        # DB가 새로 다운로드되면 인덱스도 재구성해야 함
        if os.path.exists('bm25_index.pkl'): os.remove('bm25_index.pkl')
        if os.path.exists('ontology_vectors.pkl'): os.remove('ontology_vectors.pkl')
    except Exception as e:
        print(f"DB 다운로드 실패: {e}")
 
    try:
        from backend.check_railway_db import check_db
        check_db()
    except Exception as e:
        print("Could not run check_railway_db:", e)
 
    # DB 재다운로드 시 JSON 캐시도 초기화
    if force_redownload or last_url != url:
        cache_file = 'candidates_cache_jd.json'
        if os.path.exists(cache_file):
            os.remove(cache_file)
            print("JSON 캐시 삭제 완료: candidates_cache_jd.json")

    # Ensure Auth DB is initialized (Users table, default users)
    try:
        import init_auth_db
        print("Auth DB 초기화 확인 중...")
        init_auth_db.init_db()
    except Exception as e:
        print(f"Auth DB 초기화 실패: {e}")

def ensure_indexes():
    """Ensure BM25 and Ontology Vector indexes exist."""
    import os
    
    # 1. BM25 Index
    if not os.path.exists('bm25_index.pkl'):
        print("BM25 인덱스 생성 중...")
        try:
            import build_bm25_index
            build_bm25_index.build()
        except Exception as e:
            print(f"BM25 인덱스 생성 실패: {e}")
            
    # 2. Ontology Vector Index
    if not os.path.exists('ontology_vectors.pkl'):
        print("Ontology Vector 인덱스 생성 중...")
        try:
            import build_ontology_vector
            build_ontology_vector.build_vector_map("ontology_vectors.pkl")
        except Exception as e:
            print(f"Ontology Vector 인덱스 생성 실패: {e}")




if __name__ == '__main__':
    ensure_db()
    ensure_indexes()
    import uvicorn
