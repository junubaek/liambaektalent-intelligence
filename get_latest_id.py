
import json
from connectors.gdrive_api import GDriveConnector
import datetime

gdrive = GDriveConnector()
with open('secrets.json', 'r', encoding='utf-8') as f:
    secrets = json.load(f)

folder_id = secrets.get('GOOGLE_DRIVE_FOLDER_ID')

# List files in the folder, ordered by modified time descending
res = gdrive.service.files().list(
    q=f"'{folder_id}' in parents and name contains 'candidates_reparsed_' and trashed=false",
    fields='files(id, name, modifiedTime)',
    orderBy='modifiedTime desc',
    pageSize=1
).execute()

if res.get('files'):
    latest = res['files'][0]
    print(f"Latest File Name: {latest['name']}")
    print(f"Latest File ID: {latest['id']}")
    print(f"Download URL: https://docs.google.com/uc?export=download&id={latest['id']}")
else:
    print('Not found')
