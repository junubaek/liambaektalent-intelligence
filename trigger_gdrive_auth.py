
import os
import sys
import json

# Define base project path
PROJECT_ROOT = r"C:\Users\cazam\Downloads\이력서자동분석검색시스템"
sys.path.append(PROJECT_ROOT)

from connectors.gdrive_api import GDriveConnector

def get_auth_url():
    secrets_path = os.path.join(PROJECT_ROOT, "secrets.json")
    try:
        # This will trigger the run_local_server which prints the URL to stdout
        connector = GDriveConnector(secrets_path=secrets_path)
        print("AUTH_SUCCESS")
    except Exception as e:
        print(f"AUTH_ERROR: {e}")

if __name__ == "__main__":
    get_auth_url()
