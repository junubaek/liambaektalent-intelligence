import os
import sys
sys.path.append(r"C:\Users\cazam\Downloads\이력서자동분석검색시스템")
sys.stdout.reconfigure(encoding='utf-8')

from incremental_ingest_v10 import process_file, init_db

def main():
    print("Initiating Targeted Ingestion for the 2 newly added resumes...")
    init_db()
    
    dir_path = r"C:\Users\cazam\Downloads\02_resume 전처리"
    if not os.path.exists(dir_path):
        print(f"Directory not found: {dir_path}")
        return
        
    # 파일들을 수정 시간 내림차순으로 정렬
    files = [os.path.join(dir_path, f) for f in os.listdir(dir_path) 
             if f.endswith(('.pdf', '.docx', '.doc')) and not f.startswith('~$')]
    files.sort(key=os.path.getmtime, reverse=True)
    
    # 최근 수정된 2개 파일 선택
    target_files = files[:2]
    
    print("Selected Target Resumes:")
    for tf in target_files:
        print(f"  - {os.path.basename(tf)}")
        
    success = 0
    skipped = 0
    
    for idx, fp in enumerate(target_files, 1):
        filename = os.path.basename(fp)
        print(f"\n[{idx}/2] Ingesting: {filename}...")
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
            
    print(f"\nTargeted Ingestion Complete! Success: {success} | Skipped/Failed: {skipped}")

if __name__ == "__main__":
    main()
