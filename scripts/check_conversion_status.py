
import os
import datetime

TARGET_DIR = r"C:\Users\cazam\Downloads\02_resume_converted_v8"

def check():
    if not os.path.exists(TARGET_DIR):
        print("Target dir not found.")
        return
    
    files = [f for f in os.listdir(TARGET_DIR) if f.endswith(".docx")]
    print(f"COUNT: {len(files)}")
    
    # Get last 5 modified
    file_stats = []
    for f in files:
        path = os.path.join(TARGET_DIR, f)
        mtime = os.path.getmtime(path)
        file_stats.append((f, mtime))
    
    file_stats.sort(key=lambda x: x[1], reverse=True)
    
    print("\nLast 5 modified:")
    for name, mtime in file_stats[:5]:
        dt = datetime.datetime.fromtimestamp(mtime)
        print(f"  {name} | {dt}")

if __name__ == "__main__":
    check()
