import os

def main():
    paths = [
        r'C:\Users\cazam\Downloads\02_resume 전처리',
        r'C:\Users\cazam\Downloads\02_resume_converted_v8'
    ]
    
    search_terms = ['백명석', '류혁곤']
    
    print("Searching local resume folders:")
    for path in paths:
        if not os.path.exists(path):
            print(f"  Path does not exist: {path}")
            continue
        print(f"  Searching in: {path}")
        files = os.listdir(path)
        for f in files:
            for term in search_terms:
                if term in f:
                    print(f"    [MATCH] {f}")

if __name__ == '__main__':
    main()
