import json

def read_api_response():
    for encoding in ['utf-8', 'utf-16', 'utf-16-le', 'cp949']:
        try:
            with open('api_response.json', 'r', encoding=encoding) as f:
                content = f.read(500)
                print(f"--- Encoding: {encoding} ---")
                print(content)
                return
        except Exception:
            continue
    print("Failed to read api_response.json with known encodings.")

if __name__ == "__main__":
    read_api_response()
