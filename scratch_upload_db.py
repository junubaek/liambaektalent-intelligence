import json
from connectors.gdrive_api import GDriveConnector
from googleapiclient.http import MediaFileUpload

gdrive = GDriveConnector()
with open('secrets.json', 'r', encoding='utf-8') as f:
    secrets = json.load(f)

folder_id = secrets.get('GOOGLE_DRIVE_FOLDER_ID')
print('Folder ID:', folder_id)

res = gdrive.service.files().list(q="name='candidates.db' and trashed=false", fields='files(id, name)').execute()
files = res.get('files', [])

media = MediaFileUpload('candidates.db', resumable=True)

if files:
    file_id = files[0]['id']
    print('Updating existing DB in Drive:', file_id)
    gdrive.service.files().update(fileId=file_id, media_body=media).execute()
else:
    print('Creating new DB in Drive...')
    gdrive.service.files().create(body={'name': 'candidates.db', 'parents': [folder_id]}, media_body=media).execute()

print('Upload complete.')
