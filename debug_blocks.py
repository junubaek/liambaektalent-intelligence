import traceback
from app.database import SessionLocal
from connectors.notion_api import HeadhunterDB
from sqlalchemy import text
import json

db=SessionLocal()
notion=HeadhunterDB()
q="SELECT id, name_kr FROM candidates WHERE is_duplicate=0 AND (google_drive_url IS NULL OR google_drive_url = '') LIMIT 1"
res = db.execute(text(q)).fetchone()
cid, name = res[0], res[1]
print(cid, name)
p=notion.client._request('GET', f'pages/{cid}')
print(json.dumps(p, indent=2))
