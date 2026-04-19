import sys
PROJECT_ROOT = r"C:\Users\cazam\Downloads\이력서자동분석검색시스템"
sys.path.append(PROJECT_ROOT)
from connectors.notion_api import HeadhunterDB
print(list(HeadhunterDB().fetch_candidates(limit=1)[0].keys()))
