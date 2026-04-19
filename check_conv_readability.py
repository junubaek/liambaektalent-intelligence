
import os
from docx import Document

DIR_CONV = r"C:\Users\cazam\Downloads\02_resume_converted_docx"

def check_readability():
    files = [f for f in os.listdir(DIR_CONV) if f.endswith(".docx") and not f.startswith("~$")]
    print(f"Checking readability for {len(files)} files...")
    
    empty_count = 0
    short_count = 0
    ok_count = 0
    
    for i, f in enumerate(files):
        if i % 50 == 0: print(f"  Progress: {i}/{len(files)}...")
        filepath = os.path.join(DIR_CONV, f)
        try:
            doc = Document(filepath)
            text_parts = []
            for p in doc.paragraphs:
                try:
                    text_parts.append(p.text)
                except:
                    continue
            text = "\n".join(text_parts)
            
            if not text.strip():
                empty_count += 1
            elif len(text.strip()) < 150:
                short_count += 1
            else:
                ok_count += 1
        except Exception as e:
            # print(f"  Error reading {f}: {e}")
            empty_count += 1

    print(f"\nSummary:")
    print(f"  ✅ OK (>150 chars): {ok_count}")
    print(f"  ⚠️ Short (<150 chars): {short_count}")
    print(f"  ❌ Empty/Error: {empty_count}")

if __name__ == "__main__":
    check_readability()
