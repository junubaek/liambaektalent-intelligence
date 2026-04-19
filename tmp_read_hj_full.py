import os
import sqlite3
import json
import sys
from docx import Document

# Minimal text extraction
def get_text(p):
    doc = Document(p)
    return "\n".join([para.text for para in doc.paragraphs])

if __name__ == "__main__":
    path = r"C:\Users\cazam\Downloads\02_resume 전처리\[NC] 현종민(IR)부문_86.docx"
    txt = get_text(path)
    # Search for key terms
    print(f"--- Full Text Sample (Last 5000 chars) ---")
    print(txt[-5000:])
    print(f"\n--- Full Text Sample (Total Length: {len(txt)}) ---")
