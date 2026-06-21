import os
import sys
import sqlite3
import hashlib
sys.path.append(r"C:\Users\cazam\Downloads\이력서자동분석검색시스템")
sys.stdout.reconfigure(encoding='utf-8')

from incremental_ingest_v10 import process_file, init_db, extract_text, DB_PATH

def main():
    print("Initiating Directory Ingestion for '02_resume 전처리'...")
    init_db()
    
    dir_path = r"C:\Users\cazam\Downloads\02_resume 전처리"
    if not os.path.exists(dir_path):
        print(f"Directory not found: {dir_path}")
        return
        
    all_files = [os.path.join(dir_path, f) for f in os.listdir(dir_path)
                 if f.endswith(('.pdf', '.docx', '.doc')) and not f.startswith('~$')]
                 
    print(f"Total files found in target folder: {len(all_files)}")
    
    # SQLite 연결해서 기존 MD5 캐시 가져와서 초고속 필터링
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    existing_hashes = set(row[0] for row in c.execute('SELECT document_hash FROM candidates WHERE document_hash IS NOT NULL').fetchall())
    conn.close()
    
    new_files = []
    for fp in all_files:
        text = extract_text(fp)
        if len(text) < 50:
            continue
        doc_hash = hashlib.md5(text.encode('utf-8')).hexdigest()
        if doc_hash not in existing_hashes:
            new_files.append(fp)
            
    print(f"Filtered New/Modified Resumes: {len(new_files)}")
    for nf in new_files:
        print(f"  - {os.path.basename(nf)}")
        
    if not new_files:
        print("No new resumes to process. Ingest aborted.")
        return
        
    success = 0
    skipped = 0
    
    for idx, fp in enumerate(new_files, 1):
        filename = os.path.basename(fp)
        print(f"\n[{idx}/{len(new_files)}] Ingesting new resume: {filename}...")
        try:
            ok, res_str = process_file(fp)
            if ok:
                print(f"  ✅ [SUCCESS] {filename} -> {res_str}")
                success += 1
            else:
                print(f"  ⚠️ [SKIP/ERR] {filename} -> {res_str}")
                skipped += 1
        except Exception as e:
            print(f"  ❌ [ERROR] {filename}: {e}")
            skipped += 1
            
    print(f"\nDirectory Ingestion Complete! Success: {success} | Skipped/Failed: {skipped}")

if __name__ == "__main__":
    main()
