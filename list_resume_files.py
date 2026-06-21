import os

def main():
    paths = [
        r'C:\Users\cazam\Downloads\02_resume 전처리',
        r'C:\Users\cazam\Downloads\02_resume_converted_v8'
    ]
    
    search_terms = ['명석', '혁곤']
    
    for path in paths:
        if os.path.exists(path):
            print(f"Path: {path}")
            files = os.listdir(path)
            print(f"  Total files: {len(files)}")
            matches = [f for f in files if any(t in f for t in search_terms)]
            print(f"  Matches for {search_terms}:")
            for m in matches:
                print(f"    {m}")
            if not matches:
                print("    None")

if __name__ == '__main__':
    main()
