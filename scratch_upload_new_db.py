import json
from connectors.gdrive_api import GDriveConnector
from googleapiclient.http import MediaFileUpload
import datetime

gdrive = GDriveConnector()
with open('secrets.json', 'r', encoding='utf-8') as f:
    secrets = json.load(f)

folder_id = secrets.get('GOOGLE_DRIVE_FOLDER_ID')
media = MediaFileUpload('candidates.db', resumable=True)
name = f"candidates_reparsed_{datetime.datetime.now().strftime('%Y%m%d_%H%M')}.db"

print(f'Creating new DB {name} in Drive...')
gdrive.service.files().create(body={'name': name, 'parents': [folder_id]}, media_body=media).execute()
print('Upload complete.')
