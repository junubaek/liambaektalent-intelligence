import json
from connectors.gdrive_api import GDriveConnector

def set_public_permission():
    gdrive = GDriveConnector()
    # Get the latest file
    res = gdrive.service.files().list(
        q="name contains 'candidates_reparsed' and trashed=false",
        orderBy='createdTime desc',
        fields='files(id, name, createdTime)',
        pageSize=1
    ).execute()
    
    files = res.get('files', [])
    if not files:
        print("No files found.")
        return
        
    f = files[0]
    print(f"Setting permission for: {f['name']} ({f['id']})")
    
    # Set permission to anyone with link
    gdrive.service.permissions().create(
        fileId=f['id'],
        body={'type': 'anyone', 'role': 'reader'}
    ).execute()
    print('Public permission set successfully.')

if __name__ == "__main__":
    set_public_permission()
