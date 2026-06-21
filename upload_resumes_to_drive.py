# upload_resumes_to_drive.py
"""
Bulk upload resume files from a local directory to the Google Drive folder specified in secrets.json.

Prerequisites:
- Enable Google Drive API in a GCP project.
- Place OAuth credentials file `credentials.json` in the same directory as this script.
- First run will open a browser for authentication and save `token.json`.
"""

import os
import sys
import json
from pathlib import Path

from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

SCOPES = ["https://www.googleapis.com/auth/drive.file"]

def get_drive_service():
    creds = None
    token_path = Path("token.json")
    cred_path = Path("credentials.json")
    if token_path.exists():
        creds = Credentials.from_authorized_user_file(str(token_path), SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not cred_path.exists():
                sys.exit("credentials.json not found. Place it beside this script.")
            flow = InstalledAppFlow.from_client_secrets_file(str(cred_path), SCOPES)
            creds = flow.run_local_server(port=0)
        token_path.write_text(creds.to_json())
    return build("drive", "v3", credentials=creds)

def load_folder_id():
    with open("secrets.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    folder_id = data.get("GOOGLE_DRIVE_FOLDER_ID")
    if not folder_id:
        sys.exit("GOOGLE_DRIVE_FOLDER_ID not set in secrets.json")
    return folder_id

def list_resume_files(dir_path: Path):
    exts = {".pdf", ".doc", ".docx", ".txt"}
    return [p for p in dir_path.rglob("*") if p.suffix.lower() in exts]

def upload_file(service, file_path: Path, folder_id: str) -> str:
    file_metadata = {"name": file_path.name, "parents": [folder_id]}
    media = MediaFileUpload(str(file_path), resumable=True)
    file = service.files().create(body=file_metadata, media_body=media, fields="id").execute()
    return file.get("id")

def main():
    if len(sys.argv) != 2:
        print("Usage: python upload_resumes_to_drive.py <local_resume_dir>")
        sys.exit(1)
    local_dir = Path(sys.argv[1])
    if not local_dir.is_dir():
        sys.exit(f"{local_dir} is not a valid directory")
    service = get_drive_service()
    folder_id = load_folder_id()
    files = list_resume_files(local_dir)
    if not files:
        print("No resume files found in the given directory.")
        return
    print(f"Uploading {len(files)} files to Drive folder ID {folder_id}...")
    for f in files:
        try:
            file_id = upload_file(service, f, folder_id)
            url = f"https://drive.google.com/file/d/{file_id}/view"
            print(f"Uploaded: {f.name}\n  URL: {url}")
        except Exception as e:
            print(f"Error uploading {f.name}: {e}")

if __name__ == "__main__":
    main()
