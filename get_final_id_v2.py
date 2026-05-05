import json
from connectors.gdrive_api import GDriveConnector
gdrive = GDriveConnector()
res = gdrive.service.files().list(q="name='candidates_reparsed_20260506_0252.db' and trashed=false", fields='files(id, name)').execute()
if res.get('files'):
    file_id = res['files'][0]['id']
    # Make public
    gdrive.service.permissions().create(fileId=file_id, body={'type': 'anyone', 'role': 'reader'}).execute()
    print(file_id)
else:
    print('Not found')
