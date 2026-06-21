from connectors.gdrive_api import GDriveConnector
gdrive = GDriveConnector()
res = gdrive.service.files().list(
    q="name = 'candidates.db' and trashed=false",
    fields='files(id, name, modifiedTime)'
).execute()
for f in res.get('files', []):
    print(f['name'], f['id'], f.get('modifiedTime'))
