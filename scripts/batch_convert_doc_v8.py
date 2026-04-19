
import os
import win32com.client as win32
import sys
import time

# Configuration
SOURCE_DIR = r"C:\Users\cazam\Downloads\02_resume 전처리"
TARGET_DIR = r"C:\Users\cazam\Downloads\02_resume_converted_v8"

if not os.path.exists(TARGET_DIR):
    os.makedirs(TARGET_DIR)

def convert_doc_to_docx():
    word = win32.gencache.EnsureDispatch('Word.Application')
    word.Visible = False
    word.DisplayAlerts = 0 # wdAlertsNone
    word.Options.ConfirmConversions = False
    
    doc_files = sorted([f for f in os.listdir(SOURCE_DIR) if f.lower().endswith(".doc") and not f.startswith("~$")])
    total = len(doc_files)
    print(f"🚀 Starting conversion of {total} .doc files...")
    
    success = 0
    fail = 0
    
    blacklist = [
        "JY_쩐티티엔흐엉(글로벌캐스팅담당_베트남)부문_원본.doc",
        "김대용(온라인비지니스TFT)부문_원본.doc",
        "김유성(시스템.서버엔지니어)부문_원본.doc"
    ]
    
    for i, filename in enumerate(doc_files):
        if filename in blacklist:
            continue

        target_filename = os.path.splitext(filename)[0] + ".docx"
        target_path = os.path.abspath(os.path.join(TARGET_DIR, target_filename))
        
        # Skip if already exists
        if os.path.exists(target_path):
            success += 1
            continue

        print(f"  [Attempt] {filename}...")
        source_path = os.path.abspath(os.path.join(SOURCE_DIR, filename))

        try:
            # FileName, ConfirmConversions, ReadOnly, AddToRecentFiles
            doc = word.Documents.Open(source_path, False, True, False)
            doc.SaveAs(target_path, FileFormat=16) # 16 = wdFormatXMLDocument (.docx)
            doc.Close()
            success += 1
            if success % 50 == 0:
                print(f"  [Progress] {success}/{total} converted...")
        except Exception as e:
            print(f"  ❌ Error converting {filename}: {e}")
            fail += 1
            # Add to temporary session blacklist if it hangs? No, just log for now.
            
    word.Quit()
    print(f"\n✨ Conversion Complete!")
    print(f"   - Success: {success}")
    print(f"   - Failed: {fail}")
    print(f"   - Saved to: {TARGET_DIR}")

if __name__ == "__main__":
    convert_doc_to_docx()
