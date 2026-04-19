import shutil
import os

src_folder = r'C:\Users\cazam\Downloads\02_resume 전처리'
dst_folder = r'C:\Users\cazam\Downloads\02_resume_converted_v8'

files_to_copy = [
    r'재무회계_84강민성(원본).docx',
    r'[클레온]Finance Director-이종구.docx'
]

print("--- Copying Missing Resumes ---")
for f in files_to_copy:
    src_path = os.path.join(src_folder, f)
    dst_path = os.path.join(dst_folder, f)
    if os.path.exists(src_path):
        shutil.copy2(src_path, dst_path)
        print(f"Copied: {f}")
    else:
        print(f"File not found in source: {f}")

print("Done.")
