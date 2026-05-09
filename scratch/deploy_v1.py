import sys

# Add project root to path
PROJECT_ROOT = r"C:\Users\cazam\Downloads\이력서자동분석검색시스템"
sys.path.append(PROJECT_ROOT)

import os
import json
import subprocess
from connectors.gdrive_api import GDriveConnector

def deploy():
    print("Starting Deployment Cycle...")
    
    # 1. Upload DB to GDrive
    print("[1/2] Uploading candidates.db to Google Drive...")
    try:
        with open("secrets.json", "r") as f:
            secrets = json.load(f)
        folder_id = secrets.get("GOOGLE_DRIVE_FOLDER_ID")
        
        connector = GDriveConnector()
        db_path = "candidates.db"
        
        # We'll upload it as 'candidates_v10_production.db' or similar
        # But user just said 'DB 업로드', so I'll upload the main one.
        link = connector.upload_file_to_drive(db_path, folder_id, duplicate_check=False)
        print(f"  [OK] DB uploaded: {link}")
    except Exception as e:
        print(f"  [FAIL] DB upload failed: {e}")
    
    # 2. Git Push (triggers Railway)
    print("[2/2] Pushing to GitHub (triggers Railway)...")
    try:
        # Add all changed files (like the DB, although usually DB is gitignored, 
        # but let's check)
        subprocess.run(["git", "add", "."], check=True)
        subprocess.run(["git", "commit", "-m", "chore: sync 35 new candidates and update db"], check=False)
        subprocess.run(["git", "push", "origin", "main"], check=True)
        print("  [OK] Git push successful.")
    except Exception as e:
        print(f"  [FAIL] Git push failed: {e}")

if __name__ == "__main__":
    deploy()
