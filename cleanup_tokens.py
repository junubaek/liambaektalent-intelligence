
import os

def cleanup():
    search_dirs = [
        r"C:\Users\cazam\Downloads\안티그래비티",
        r"C:\Users\cazam\Downloads\이력서자동분석검색시스템"
    ]
    for d in search_dirs:
        for root, dirs, files in os.walk(d):
            if "gdrive_token.pickle" in files:
                p = os.path.join(root, "gdrive_token.pickle")
                print(f"Deleting: {p}")
                os.remove(p)

if __name__ == "__main__":
    cleanup()
