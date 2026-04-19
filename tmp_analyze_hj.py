import os
import sqlite3
import json
import sys
import PyPDF2
from docx import Document

sys.path.append(os.getcwd())
from resume_parser import ResumeParser
from connectors.openai_api import OpenAIClient

def extract_text(filepath):
    ext = os.path.splitext(filepath)[1].lower()
    text = ""
    if ext == '.pdf':
        with open(filepath, 'rb') as f:
            reader = PyPDF2.PdfReader(f)
            for page in reader.pages:
                text += page.extract_text() or ""
    elif ext == '.docx':
        doc = Document(filepath)
        text = "\n".join([para.text for para in doc.paragraphs])
    return text.strip()

def analyze_specific():
    with open("secrets.json", "r") as f:
        secrets = json.load(f)
    
    client = OpenAIClient(secrets["OPENAI_API_KEY"])
    parser = ResumeParser(client)
    
    # Found his file earlier
    path = r"C:\Users\cazam\Downloads\02_resume 전처리\[NC] 현종민(IR)부문_86.docx"
    text = extract_text(path)
    
    print("--- RAW TEXT EXTRACTED ---")
    print(text[:2000])
    
    print("\n--- AI ANALYSIS ---")
    result = parser.parse(text)
    print(json.dumps(result, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    analyze_specific()
