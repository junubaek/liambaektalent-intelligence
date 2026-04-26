from connectors.gdrive_api import GDriveConnector
import json

gdrive = GDriveConnector()
res = gdrive.service.files().list(
    q="name contains 'candidates_reparsed' and trashed=false",
    orderBy='createdTime desc',
    fields='files(id, name, createdTime)',
    pageSize=5
).execute()

files = res.get('files', [])
for f in files:
    file_id = f['id']
    url = f'https://drive.google.com/uc?export=download&id={file_id}'
    print(f"{f['name']}")
    print(f'URL: {url}')
    print()
