import sys
import json
PROJECT_ROOT = r"C:\Users\cazam\Downloads\이력서자동분석검색시스템"
sys.path.append(PROJECT_ROOT)
from connectors.notion_api import HeadhunterDB

db = HeadhunterDB()
db_id = db.client.search_db_by_name("Vector DB")
if not db_id:
    db_id = db.client.search_db_by_name("DB")

res = db.client._request("GET", f"databases/{db_id}")
props = res.get("properties", {})

for k in ['Primary Sector', 'Domain', 'Role Cluster']:
    if k in props and 'select' in props[k]:
        opts = [o["name"] for o in props[k]["select"].get("options", [])]
        print(f"{k} = {opts}")
