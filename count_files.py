import os
folders = {
    "원본": r"C:\\Users\\cazam\\Downloads\\02_resume 전처리",
    "변환본": r"C:\\Users\\cazam\\Downloads\\02_resume_converted_v8",
}
for name, path in folders.items():
    if os.path.isdir(path):
        files = [f for f in os.listdir(path) if f.lower().endswith(('.pdf', '.docx', '.doc', '.txt')) and not f.startswith('~$')]
        print(f"{name}: {len(files)}")
    else:
        print(f"{name}: 폴더 없음")
