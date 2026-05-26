import json
import sys
import os
from connectors.gdrive_api import GDriveConnector
from googleapiclient.http import MediaFileUpload

# Set stdout to UTF-8
sys.stdout.reconfigure(encoding='utf-8')

PROJECT_ROOT = r"C:\Users\cazam\Downloads\이력서자동분석검색시스템"
os.chdir(PROJECT_ROOT)

def upload_fresh():
    gdrive = GDriveConnector()
    with open('secrets.json', 'r', encoding='utf-8') as f:
        secrets = json.load(f)

    folder_id = secrets.get('GOOGLE_DRIVE_FOLDER_ID')
    db_path = 'candidates.db'
    
    print(f"Creating a BRAND NEW candidates.db file in Google Drive folder: {folder_id}...")
    media = MediaFileUpload(db_path, resumable=True)
    
    file_metadata = {
        'name': 'candidates.db',
        'parents': [folder_id]
    }
    
    # Force creation of a new file to get a fresh File ID
    res = gdrive.service.files().create(body=file_metadata, media_body=media).execute()
    new_file_id = res.get('id')
    
    print("\n==================================================")
    print("✅ [최신 DB 신규 업로드 완료]")
    print("==================================================")
    print(f"새로운 Google Drive 파일 ID: {new_file_id}")
    print(f"새로운 Railway DB_DOWNLOAD_URL 설정 값:")
    print(f"https://drive.google.com/uc?export=download&id={new_file_id}")
    print("==================================================")

if __name__ == "__main__":
    upload_fresh();
