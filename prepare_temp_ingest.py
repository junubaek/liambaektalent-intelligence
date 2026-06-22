import os, sys, shutil

# Create temporary directory for targeted ingestion
TEMP_DIR = r"C:\Users\cazam\Downloads\이력서자동분석검색시스템\temp_target_resumes"
if os.path.exists(TEMP_DIR):
    shutil.rmtree(TEMP_DIR)
os.makedirs(TEMP_DIR)

# Copy the two target resume files to the temp directory
targets = [
    r"C:\Users\cazam\Downloads\02_resume 전처리\[이형무] 이형무(Silicon Validation Engineer)이력서.pdf",
    r"C:\Users\cazam\Downloads\02_resume 전처리\[이겨례] 이겨례(TPM)이력서.pdf"
]

for t in targets:
    shutil.copy(t, TEMP_DIR)

print(f"Copied target resumes to {TEMP_DIR}")
