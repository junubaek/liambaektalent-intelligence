import os

def read_utf16_file(path):
    try:
        with open(path, 'r', encoding='utf-16') as f:
            print(f.read())
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    read_utf16_file('available_models.txt')
