import json
import os
import datetime
from connectors.gdrive_api import GDriveConnector
from googleapiclient.http import MediaFileUpload

def upload_and_share():
    gdrive = GDriveConnector()
    with open('secrets.json', 'r', encoding='utf-8') as f:
        secrets = json.load(f)

    folder_id = secrets.get('GOOGLE_DRIVE_FOLDER_ID')
    db_file = 'candidates.db'
    
    if not os.path.exists(db_file):
        print(f"Error: {db_file} not found.")
        return

    name = f"candidates_reparsed_{datetime.datetime.now().strftime('%Y%m%d_%H%M')}.db"
    media = MediaFileUpload(db_file, mimetype='application/x-sqlite3', resumable=True)

    print(f'Uploading {db_file} as {name}...')
    file = gdrive.service.files().create(
        body={'name': name, 'parents': [folder_id]},
        media_body=media,
        fields='id'
    ).execute()
    
    file_id = file.get('id')
    print(f'Upload complete. File ID: {file_id}')

    print('Setting permissions to anyone (reader)...')
    gdrive.service.permissions().create(
        fileId=file_id,
        body={'type': 'anyone', 'role': 'reader'}
    ).execute()
    print('Permissions updated.')

    download_url = f"https://drive.google.com/uc?export=download&id={file_id}"
    print(f'Direct Download URL: {download_url}')
    
    # Save to a temp file for verification if needed
    with open('latest_db_id.txt', 'w') as f:
        f.write(file_id)

if __name__ == "__main__":
    upload_and_share()
