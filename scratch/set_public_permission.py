import json
from connectors.gdrive_api import GDriveConnector

def set_public_permission():
    gdrive = GDriveConnector()
    file_id = "1q2LHW3EF2_IK_5gPjhiUAzGASjvjCQ0E"
    
    print(f"Setting public permission for File ID: {file_id}")
    
    # Set permission to anyone with link
    gdrive.service.permissions().create(
        fileId=file_id,
        body={'type': 'anyone', 'role': 'reader'}
    ).execute()
    print('Public permission set successfully.')

if __name__ == "__main__":
    set_public_permission()
