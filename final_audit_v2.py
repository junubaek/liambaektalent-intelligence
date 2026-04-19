import json
import requests

def audit():
    with open('secrets.json', 'r') as f:
        secrets = json.load(f)
    
    NOTION_API_KEY = secrets['NOTION_API_KEY']
    DATABASE_ID = secrets['NOTION_DATABASE_ID']
    
    headers = {
        "Authorization": f"Bearer {NOTION_API_KEY}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28"
    }
    
    url = f"https://api.notion.com/v1/databases/{DATABASE_ID}/query"
    
    def count_missing_multi_select(property_name):
        total_missing = 0
        has_more = True
        next_cursor = None
        filter_payload = {
            "property": property_name,
            "multi_select": {
                "is_empty": True
            }
        }
        while has_more:
            payload = {"filter": filter_payload, "page_size": 100}
            if next_cursor:
                payload["start_cursor"] = next_cursor
            response = requests.post(url, headers=headers, json=payload)
            data = response.json()
            if "results" not in data:
                print(f"Error checking {property_name}: {data}")
                break
            total_missing += len(data.get("results", []))
            has_more = data.get("has_more", False)
            next_cursor = data.get("next_cursor")
        return total_missing

    def count_missing_rich_text(property_name):
        total_missing = 0
        has_more = True
        next_cursor = None
        filter_payload = {
            "property": property_name,
            "rich_text": {
                "is_empty": True
            }
        }
        while has_more:
            payload = {"filter": filter_payload, "page_size": 100}
            if next_cursor:
                payload["start_cursor"] = next_cursor
            response = requests.post(url, headers=headers, json=payload)
            data = response.json()
            if "results" not in data:
                print(f"Error checking {property_name}: {data}")
                break
            total_missing += len(data.get("results", []))
            has_more = data.get("has_more", False)
            next_cursor = data.get("next_cursor")
        return total_missing

    def count_missing_number(property_name):
        total_missing = 0
        has_more = True
        next_cursor = None
        filter_payload = {
            "property": property_name,
            "number": {
                "is_empty": True
            }
        }
        while has_more:
            payload = {"filter": filter_payload, "page_size": 100}
            if next_cursor:
                payload["start_cursor"] = next_cursor
            response = requests.post(url, headers=headers, json=payload)
            data = response.json()
            if "results" not in data:
                print(f"Error checking {property_name}: {data}")
                break
            total_missing += len(data.get("results", []))
            has_more = data.get("has_more", False)
            next_cursor = data.get("next_cursor")
        return total_missing

    missing_patterns = count_missing_multi_select("Experience Patterns")
    missing_summaries = count_missing_rich_text("경력 Summary")
    missing_scores = count_missing_number("v6.2 Score")

    print(f"\nCOMPREHENSIVE AUDIT RESULTS (ALL CANDIDATES):")
    print(f"Missing Experience Patterns: {missing_patterns}")
    print(f"Missing 경력 Summary: {missing_summaries}")
    print(f"Missing v6.2 Score: {missing_scores}")

if __name__ == "__main__":
    audit()
