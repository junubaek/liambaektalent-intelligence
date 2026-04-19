import json
from data_curator import DataCurator
from connectors.gemini_api import GeminiClient

curator = DataCurator()
candidates = curator.diagnose_db(limit=1)
if candidates:
    print(f"Testing on candidate: {candidates[0].get('name')}")
    success = curator.repair_candidate(candidates[0])
    print(f"Repair Success: {success}")
else:
    print("No blanks found to test. Trying a random recent candidate.")
    res = curator.client.query_database(curator.secrets.get('NOTION_DATABASE_ID'), limit=1)
    if res.get('results'):
        props = curator.client.extract_properties(res['results'][0])
        print(f"Testing on candidate: {props.get('name')}")
        success = curator.repair_candidate(props)
        print(f"Repair Success: {success}")
