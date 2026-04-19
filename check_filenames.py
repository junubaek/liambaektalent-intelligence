import json
from connectors.notion_api import HeadhunterDB

notion = HeadhunterDB()

# 1. 리나 (데이터분석)
page1 = notion.client._request("GET", "pages/33522567-1b6f-81d1-84b4-d80fff34b631")
if page1 and "error" not in page1:
    title1 = page1.get("properties", {}).get("파일명", {}).get("title", [{}])[0].get("plain_text", "NO TITLE")
    print(f"리나 파일명: {title1}")
else:
    print("리나: 404 or Error")

# 2. 어울림
page2 = notion.client._request("GET", "pages/69832170-515b-40b6-95f4-65de96656665")
if page2 and "error" not in page2:
    title2 = page2.get("properties", {}).get("파일명", {}).get("title", [{}])[0].get("plain_text", "NO TITLE")
    print(f"어울림 파일명: {title2}")
else:
    print("어울림: 404 or Error (Notion에서 삭제되거나 권한 없음)")

# Fallback: check SQLite raw text or previous json? We just want the Filename which comes from Notion.
