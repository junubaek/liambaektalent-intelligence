import sys
import os
sys.path.append(os.path.abspath('connectors'))
from gdrive_api import GDriveConnector

try:
    connector = GDriveConnector()
    file_id = '11eT2aLCbdEVJzNAUC-Xmnf2M13lDO0AO'
    file_meta = connector.service.files().get(fileId=file_id, fields='name').execute()
    with open('filename_out.txt', 'w', encoding='utf-8') as f:
        f.write(file_meta.get('name', 'N/A'))
except Exception as e:
    with open('filename_out.txt', 'w', encoding='utf-8') as f:
        f.write('Error: ' + str(e))
