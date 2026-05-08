import json
import re
from connectors.gdrive_api import GDriveConnector

def inspect_targets():
    with open('reparse_targets.json', 'r', encoding='utf-8') as f:
        targets = json.load(f)
        
    gdrive = GDriveConnector()
    
    print(f"{'Name':<10} | {'MimeType':<40} | {'Size':<10} | {'FileID'}")
    print("-" * 80)
    
    for t in targets:
        url = t['google_drive_url']
        match = re.search(r'/d/([a-zA-Z0-9_-]+)', url)
        if not match:
            print(f"{t['name_kr']:<10} | Invalid URL")
            continue
        file_id = match.group(1)
        
        try:
            file_meta = gdrive.service.files().get(fileId=file_id, fields="name, mimeType, size").execute()
            name = file_meta.get('name', 'N/A')
            mime = file_meta.get('mimeType', 'N/A')
            size = file_meta.get('size', 'N/A')
            print(f"{t['name_kr']:<10} | {mime:<40} | {size:<10} | {file_id}")
        except Exception as e:
            print(f"{t['name_kr']:<10} | Error: {e}")

if __name__ == "__main__":
    inspect_targets()
