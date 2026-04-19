import os
import glob

def fix_encoding(directory):
    for filepath in glob.glob(os.path.join(directory, "*.py")):
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                f.read()
        except UnicodeDecodeError:
            try:
                # Read with CP949 or EUC-KR
                with open(filepath, 'r', encoding='cp949') as f:
                    content = f.read()
                # Write back with UTF-8
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(content)
                print(f"Fixed: {filepath}")
            except Exception as e:
                print(f"Failed to fix {filepath}: {e}")

if __name__ == "__main__":
    fix_encoding(".")
