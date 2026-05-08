import sqlite3
import json
import os
import re
import io
import time
from connectors.gdrive_api import GDriveConnector
from connectors.gemini_api import GeminiClient
from resume_parser import ResumeParser
from googleapiclient.http import MediaIoBaseDownload

def extract_text_from_office_via_gdrive(gdrive, file_id, file_name, mime_type):
    """
    For DOCX/DOC files: Copy to Google Docs format, export as text, then delete the copy.
    This is the most reliable way to extract text from Office files via GDrive.
    """
    try:
        # Step 1: Copy file as Google Docs format
        copy_metadata = {
            'name': f'_temp_convert_{file_name}',
            'mimeType': 'application/vnd.google-apps.document'
        }
        copied_file = gdrive.service.files().copy(
            fileId=file_id,
            body=copy_metadata,
            fields='id'
        ).execute()
        copy_id = copied_file['id']
        print(f"    Created Google Docs copy: {copy_id}")
        
        try:
            # Step 2: Export the Google Docs copy as plain text
            response = gdrive.service.files().export(
                fileId=copy_id, 
                mimeType='text/plain'
            ).execute()
            text = response.decode('utf-8') if isinstance(response, bytes) else response
            print(f"    Exported text: {len(text)} chars")
            return text
        finally:
            # Step 3: Always clean up - delete the temporary copy
            try:
                gdrive.service.files().delete(fileId=copy_id).execute()
                print(f"    Cleaned up temp copy")
            except Exception:
                pass
                
    except Exception as e:
        print(f"    GDocs convert/export error: {e}")
        return None


def deep_reextract_all():
    """Process all 33 candidates from candidates_to_delete.json"""
    
    with open('candidates_to_delete.json', 'r', encoding='utf-8') as f:
        all_targets = json.load(f)
        
    with open('secrets.json', 'r', encoding='utf-8') as f:
        secrets = json.load(f)
        
    gdrive = GDriveConnector()
    gemini = GeminiClient(secrets['GEMINI_API_KEY'])
    parser = ResumeParser(gemini)
    
    conn = sqlite3.connect('candidates.db')
    cursor = conn.cursor()
    
    # Check which ones still need work
    targets = []
    for t in all_targets:
        cid = t['id']
        cursor.execute("""
            SELECT is_parsed, LENGTH(raw_text) as text_len, sector, LENGTH(profile_summary) as sum_len
            FROM candidates WHERE id = ?
        """, (cid,))
        row = cursor.fetchone()
        if row:
            is_parsed, text_len, sector, sum_len = row
            text_len = text_len or 0
            sum_len = sum_len or 0
            if is_parsed and text_len > 200 and sum_len > 10 and sector:
                continue  # Already OK
        targets.append(t)
    
    print(f"=== Deep Processing {len(targets)}/{len(all_targets)} remaining targets ===\n")
    
    success = 0
    fail = 0
    fail_list = []
    
    for i, t in enumerate(targets, 1):
        cid = t['id']
        name = t['name_kr']
        url = t.get('google_drive_url', '')
        
        print(f"\n[{i}/{len(targets)}] [{name}] ({cid[:16]}...)")
        
        if not url:
            print(f"  [SKIP] No GDrive URL")
            fail += 1
            fail_list.append(f"{name}: No URL")
            continue
        
        try:
            # Extract file ID
            match = re.search(r'/d/([a-zA-Z0-9_-]+)', url)
            if not match:
                print(f"  [SKIP] Invalid URL")
                fail += 1
                fail_list.append(f"{name}: Invalid URL")
                continue
            file_id = match.group(1)
            
            # Get file metadata
            file_meta = gdrive.service.files().get(fileId=file_id, fields="name, mimeType").execute()
            mime_type = file_meta.get('mimeType', '')
            file_name = file_meta.get('name', '')
            print(f"  {file_name} ({mime_type})")
            
            full_text = None
            result = None
            
            # === PDF ===
            if mime_type == 'application/pdf':
                full_text = gdrive.extract_text_from_url(url)
                
                if full_text and len(full_text) > 200:
                    print(f"  [PDF] PyPDF2 OK ({len(full_text)} chars)")
                    result = parser.parse(full_text)
                else:
                    print(f"  [PDF] PyPDF2 weak. Gemini Multimodal...")
                    file_bytes, _, _ = gdrive.download_file(url)
                    if file_bytes:
                        result = parser.parse_multimodal(file_bytes, 'application/pdf')
                        if result:
                            full_text = result.get('candidate_profile', {}).get('raw_text_full', full_text or '')
                            
            # === DOCX/DOC ===
            elif mime_type in ('application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                              'application/msword'):
                # Strategy: Copy file as Google Docs -> Export as text
                print(f"  [DOC] Converting via Google Docs copy...")
                full_text = extract_text_from_office_via_gdrive(gdrive, file_id, file_name, mime_type)
                
                if not full_text or len(full_text) < 100:
                    # Fallback: python-docx (only for .docx)
                    if 'openxmlformats' in mime_type:
                        print(f"  [DOC] Trying python-docx fallback...")
                        try:
                            from docx import Document
                            request = gdrive.service.files().get_media(fileId=file_id)
                            fh = io.BytesIO()
                            downloader = MediaIoBaseDownload(fh, request)
                            done = False
                            while not done:
                                _, done = downloader.next_chunk()
                            fh.seek(0)
                            doc = Document(fh)
                            full_text = "\n".join([p.text for p in doc.paragraphs if p.text.strip()])
                            if full_text:
                                print(f"  python-docx OK ({len(full_text)} chars)")
                        except Exception as docx_err:
                            print(f"  python-docx failed: {docx_err}")
                
                if full_text and len(full_text) > 100:
                    print(f"  Parsing text ({len(full_text)} chars)...")
                    result = parser.parse(full_text)
                else:
                    print(f"  [FAIL] No usable text")
                    fail += 1
                    fail_list.append(f"{name}: No text from DOCX")
                    continue
                    
            # === Google Docs (native) ===
            elif mime_type == 'application/vnd.google-apps.document':
                response = gdrive.service.files().export(fileId=file_id, mimeType='text/plain').execute()
                full_text = response.decode('utf-8') if isinstance(response, bytes) else response
                if full_text and len(full_text) > 100:
                    result = parser.parse(full_text)
                    
            else:
                print(f"  [SKIP] Unsupported: {mime_type}")
                fail += 1
                fail_list.append(f"{name}: Unsupported MIME {mime_type}")
                continue
            
            # === Update DB ===
            if result:
                profile = result.get('candidate_profile', {})
                patterns = result.get('patterns', [])
                careers_json = json.dumps(patterns, ensure_ascii=False)
                
                if full_text:
                    cursor.execute("UPDATE candidates SET raw_text = ? WHERE id = ?", (full_text, cid))
                
                main_sectors = profile.get('main_sectors', [])
                sector_str = ", ".join(main_sectors) if isinstance(main_sectors, list) else str(main_sectors or '')
                
                exp_summary = profile.get('experience_summary', '')
                summary_str = "\n".join(exp_summary) if isinstance(exp_summary, list) else str(exp_summary or '')
                
                cursor.execute("""
                    UPDATE candidates 
                    SET is_parsed = 1, careers_json = ?, total_years = ?,
                        sector = ?, profile_summary = ?, updated_at = datetime('now')
                    WHERE id = ?
                """, (careers_json, profile.get('total_years_experience', 0), sector_str, summary_str, cid))
                
                conn.commit()
                print(f"  [OK] {name} -> {sector_str}")
                success += 1
            else:
                print(f"  [FAIL] No parse result")
                fail += 1
                fail_list.append(f"{name}: Parse failed")
                conn.commit()
                
        except Exception as e:
            print(f"  [ERROR] {e}")
            fail += 1
            fail_list.append(f"{name}: {e}")
            conn.commit()
        
        time.sleep(1)
        
    conn.close()
    print(f"\n{'='*50}")
    print(f"=== COMPLETE ===")
    print(f"  Success: {success}/{len(targets)}")
    print(f"  Failed:  {fail}/{len(targets)}")
    if fail_list:
        print(f"\nFailed candidates:")
        for f in fail_list:
            print(f"  - {f}")

if __name__ == "__main__":
    deep_reextract_all()
