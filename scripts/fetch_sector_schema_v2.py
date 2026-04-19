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

print(f"Properties keys: {list(props.keys())}")

main_sectors = []
if "Main Sector" in props and "select" in props["Main Sector"]:
    main_sectors = [opt["name"] for opt in props["Main Sector"]["select"].get("options", [])]

sub_sectors = []
if "Sub Sector" in props and "select" in props["Sub Sector"]:
    sub_sectors = [opt["name"] for opt in props["Sub Sector"]["select"].get("options", [])]
    
print(f"MAIN_SECTORS = {main_sectors}")
print(f"SUB_SECTORS = {sub_sectors}")
