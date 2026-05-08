import sqlite3
import json
import os
import re
import io
from connectors.gdrive_api import GDriveConnector
from connectors.gemini_api import GeminiClient
from resume_parser import ResumeParser

def deep_reextract_and_parse():
    # 1. Load targets
    with open('reparse_targets.json', 'r', encoding='utf-8') as f:
        targets = json.load(f)
        
    if not os.path.exists('secrets.json'):
        print("secrets.json not found.")
        return
        
    with open('secrets.json', 'r', encoding='utf-8') as f:
        secrets = json.load(f)
        
    # 2. Initialize Clients
    gdrive = GDriveConnector()
    gemini = GeminiClient(secrets['GEMINI_API_KEY'])
    parser = ResumeParser(gemini)
    
    conn = sqlite3.connect('candidates.db')
    cursor = conn.cursor()
    
    success_count = 0
    fail_count = 0
    
    print(f"--- Deep Processing {len(targets)} Targets ---")
    
    for t in targets:
        cid = t['id']
        name = t['name_kr']
        url = t['google_drive_url']
        
        print(f"\nProcessing [{name}] ({cid})...")
        
        try:
            # Extract file ID from URL
            match = re.search(r'/d/([a-zA-Z0-9_-]+)', url)
            if not match:
                print(f"  [SKIP] Could not extract file ID from URL")
                fail_count += 1
                continue
            file_id = match.group(1)
            
            # Get file metadata to check MIME type
            file_meta = gdrive.service.files().get(fileId=file_id, fields="name, mimeType").execute()
            mime_type = file_meta.get('mimeType', '')
            file_name = file_meta.get('name', '')
            print(f"  File: {file_name} ({mime_type})")
            
            full_text = None
            result = None
            
            # === Strategy by MIME type ===
            
            if mime_type == 'application/pdf':
                # PDF: Try PyPDF2 first, fallback to Gemini Multimodal
                print(f"  [PDF] Trying text extraction...")
                full_text = gdrive.extract_text_from_url(url)
                
                if full_text and len(full_text) > 200:
                    print(f"  Text extraction OK ({len(full_text)} chars). Parsing...")
                    result = parser.parse(full_text)
                else:
                    print(f"  Text extraction weak ({len(full_text) if full_text else 0} chars). Using Gemini Multimodal...")
                    file_bytes, _, _ = gdrive.download_file(url)
                    if file_bytes:
                        result = parser.parse_multimodal(file_bytes, 'application/pdf')
                        if result:
                            full_text = result.get('candidate_profile', {}).get('raw_text_full', full_text or '')
                            
            elif mime_type in ('application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                              'application/msword',
                              'application/vnd.google-apps.document'):
                # DOCX/DOC/Google Doc: Export as text via Google Docs API
                print(f"  [DOC/DOCX] Exporting as text via Google Docs API...")
                try:
                    response = gdrive.service.files().export(fileId=file_id, mimeType='text/plain').execute()
                    full_text = response.decode('utf-8') if isinstance(response, bytes) else response
                    print(f"  Export success ({len(full_text)} chars).")
                except Exception as export_err:
                    print(f"  Export failed: {export_err}")
                    # Try direct docx download
                    print(f"  Trying direct download + python-docx...")
                    try:
                        from docx import Document
                        from googleapiclient.http import MediaIoBaseDownload
                        request = gdrive.service.files().get_media(fileId=file_id)
                        fh = io.BytesIO()
                        downloader = MediaIoBaseDownload(fh, request)
                        done = False
                        while not done:
                            status, done = downloader.next_chunk()
                        fh.seek(0)
                        doc = Document(fh)
                        full_text = "\n".join([p.text for p in doc.paragraphs if p.text.strip()])
                        print(f"  Direct DOCX parse success ({len(full_text)} chars).")
                    except Exception as docx_err:
                        print(f"  Direct DOCX parse also failed: {docx_err}")
                        full_text = None
                
                if full_text and len(full_text) > 100:
                    print(f"  Parsing with Gemini AI...")
                    result = parser.parse(full_text)
                else:
                    print(f"  [WARN] No usable text extracted for {name}.")
                    fail_count += 1
                    continue
            else:
                print(f"  [SKIP] Unsupported MIME type: {mime_type}")
                fail_count += 1
                continue
            
            # === Update DB ===
            if result:
                profile = result.get('candidate_profile', {})
                patterns = result.get('patterns', [])
                careers_json = json.dumps(patterns, ensure_ascii=False)
                
                # Update raw_text
                if full_text:
                    cursor.execute("UPDATE candidates SET raw_text = ? WHERE id = ?", (full_text, cid))
                
                # Get sector string
                main_sectors = profile.get('main_sectors', [])
                if isinstance(main_sectors, list):
                    sector_str = ", ".join(main_sectors)
                else:
                    sector_str = str(main_sectors) if main_sectors else ''
                
                # Get summary string
                exp_summary = profile.get('experience_summary', '')
                if isinstance(exp_summary, list):
                    summary_str = "\n".join(exp_summary)
                else:
                    summary_str = str(exp_summary) if exp_summary else ''
                
                cursor.execute("""
                    UPDATE candidates 
                    SET is_parsed = 1,
                        careers_json = ?,
                        total_years = ?,
                        sector = ?,
                        profile_summary = ?,
                        updated_at = datetime('now')
                    WHERE id = ?
                """, (
                    careers_json,
                    profile.get('total_years_experience', 0),
                    sector_str,
                    summary_str,
                    cid
                ))
                print(f"  [SUCCESS] {name} updated. Sector: {sector_str}")
                success_count += 1
            else:
                print(f"  [FAILED] Parsing returned no result for {name}.")
                fail_count += 1
                
        except Exception as e:
            print(f"  [ERROR] {name}: {e}")
            fail_count += 1
            
        conn.commit()
        
    conn.close()
    print(f"\n--- Deep Processing Complete ---")
    print(f"  Success: {success_count}/{len(targets)}")
    print(f"  Failed:  {fail_count}/{len(targets)}")

if __name__ == "__main__":
    deep_reextract_and_parse()
