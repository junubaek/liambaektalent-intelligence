import os
import json
import pickle
import io
import PyPDF2
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload

class GDriveConnector:
    def __init__(self, secrets_path=None, token_path=None):
        if secrets_path is None:
            possible_paths = [
                "secrets.json",
                os.path.join(os.path.dirname(__file__), "..", "secrets.json"),
                r"C:\Users\cazam\Downloads\이력서자동분석검색시스템\secrets.json"
            ]
            for p in possible_paths:
                if os.path.exists(p):
                    secrets_path = p
                    break
        
        if not secrets_path or not os.path.exists(secrets_path):
            raise FileNotFoundError(f"Could not find secrets.json. Tried: {secrets_path}")

        with open(secrets_path, "r") as f:
            self.secrets = json.load(f)
        
        if token_path is None:
            token_path = os.path.join(os.path.dirname(secrets_path), "gdrive_token.pickle")
        
        self.token_path = token_path
        self.creds = None
        self.scopes = ['https://www.googleapis.com/auth/drive.readonly', 'https://www.googleapis.com/auth/drive.file', 'https://www.googleapis.com/auth/drive.metadata.readonly']
        self._authenticate()
        self.service = build('drive', 'v3', credentials=self.creds)

    def _authenticate(self):
        if os.path.exists(self.token_path):
            with open(self.token_path, 'rb') as token:
                self.creds = pickle.load(token)
        
        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                from google.auth.exceptions import RefreshError
                try:
                    self.creds.refresh(Request())
                except RefreshError:
                    print("Token expired or revoked. Starting new authentication flow...")
                    os.remove(self.token_path)
                    self.creds = None
                    return self._authenticate()
            else:
                client_config = {
                    "installed": {
                        "client_id": self.secrets["GOOGLE_CLIENT_ID"],
                        "client_secret": self.secrets["GOOGLE_CLIENT_SECRET"],
                        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                        "token_uri": "https://oauth2.googleapis.com/token"
                    }
                }
                flow = InstalledAppFlow.from_client_config(client_config, self.scopes)
                self.creds = flow.run_local_server(port=8080, access_type='offline', prompt='consent')
            
            with open(self.token_path, 'wb') as token:
                pickle.dump(self.creds, token)

    def extract_text_from_url(self, gdrive_url):
        if not gdrive_url:
            return ""
            
        import re
        # Extract File ID
        match = re.search(r'/d/([a-zA-Z0-9_-]+)', gdrive_url)
        if not match:
            return ""
        file_id = match.group(1)
        
        try:
            # Check mime type
            file_meta = self.service.files().get(fileId=file_id, fields="mimeType").execute()
            mime_type = file_meta.get('mimeType', '')
            
            if 'application/vnd.google-apps.document' in mime_type:
                # Export Google Doc as Text
                response = self.service.files().export(fileId=file_id, mimeType='text/plain').execute()
                return response.decode('utf-8')
            elif 'application/pdf' in mime_type:
                # Download PDF bytes
                request = self.service.files().get_media(fileId=file_id)
                fh = io.BytesIO()
                downloader = MediaIoBaseDownload(fh, request)
                done = False
                while done is False:
                    status, done = downloader.next_chunk()
                
                fh.seek(0)
                pdf_reader = PyPDF2.PdfReader(fh)
                text = []
                for page in pdf_reader.pages:
                    extracted = page.extract_text()
                    if extracted:
                        text.append(extracted)
                return "\n".join(text)
            elif 'application/vnd.openxmlformats-officedocument.wordprocessingml.document' in mime_type or mime_type == 'application/msword':
                # Download DOCX bytes
                from docx import Document
                request = self.service.files().get_media(fileId=file_id)
                fh = io.BytesIO()
                downloader = MediaIoBaseDownload(fh, request)
                done = False
                while not done:
                    status, done = downloader.next_chunk()
                fh.seek(0)
                try:
                    doc = Document(fh)
                    text = [p.text for p in doc.paragraphs if p.text.strip()]
                    return "\n".join(text)
                except Exception as docx_e:
                    print(f"Failed to parse docx: {docx_e}")
                    return ""
            else:
                print(f"Unsupported mime_type: {mime_type}")
                return ""
        except Exception as e:
            print(f"GDrive extraction error: {e}")
            return ""

    def upload_file_to_drive(self, file_path, folder_id, duplicate_check=True):
        if not os.path.exists(file_path):
            print(f"File not found: {file_path}")
            return None
            
        filename = os.path.basename(file_path)
        
        if duplicate_check:
            query = f"'{folder_id}' in parents and name = '{filename}' and trashed = false"
            try:
                res = self.service.files().list(q=query, spaces='drive', fields='files(id, name, webViewLink)').execute()
                items = res.get('files', [])
                if items:
                    print(f"  [GDrive] File '{filename}' already exists in folder. Returning existing link.")
                    return items[0].get('webViewLink')
            except Exception as e:
                print(f"  [GDrive] Error checking duplicates: {e}")
                
        ext = os.path.splitext(filename)[1].lower()
        if ext == '.pdf':
            mimetype = 'application/pdf'
        elif ext == '.docx':
            mimetype = 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        elif ext == '.doc':
            mimetype = 'application/msword'
        else:
            mimetype = 'application/octet-stream'
            
        file_metadata = {
            'name': filename,
            'parents': [folder_id]
        }
        
        try:
            print(f"  [GDrive] Uploading new file: {filename} ...")
            media = MediaFileUpload(file_path, mimetype=mimetype, resumable=True)
            file = self.service.files().create(body=file_metadata, media_body=media, fields='id, webViewLink').execute()
            print(f"  [GDrive] Upload success -> {file.get('webViewLink')}")
            return file.get('webViewLink')
        except Exception as e:
            print(f"  [GDrive] Upload error: {e}")
            return None

if __name__ == "__main__":
    connector = GDriveConnector()
    # Test with the URL from earlier
    url = "https://docs.google.com/document/d/1-VjZwadDgMWsr5Wprt625naZCE7mExQ9/edit"
    print("Testing extraction...")
    text = connector.extract_text_from_url(url)
    print(f"Extracted {len(text)} chars. Preview:")
    print(text[:200])
