import json
from connectors.gdrive_api import GDriveConnector
gdrive = GDriveConnector()
res = gdrive.service.files().list(q="name='candidates_reparsed_20260506_0037.db' and trashed=false", fields='files(id, name)').execute()
if res.get('files'):
    print(res['files'][0]['id'])
else:
    print('Not found')
