import os
import json
import hashlib
import glob
from sqlalchemy.orm import Session
from app.database import engine, Base, SessionLocal
from app.models import Candidate, ParsingCache

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
CACHE_FILE = os.path.join(ROOT_DIR, "candidates_cache_jd.json")
PDF_DIR = os.path.abspath(os.path.join(ROOT_DIR, "02_resume 전처리"))
V8_DOCX_DIR = os.path.abspath(os.path.join(ROOT_DIR, "02_resume_converted_v8"))
CURRENT_PROMPT_VERSION = "v8.5_20260406"

def generate_logic_hash(text: str, version: str) -> str:
    combined = f"{text}|{version}"
    return hashlib.sha256(combined.encode('utf-8')).hexdigest()

def extract_text_from_file(clean_name: str) -> str:
    import re
    if not clean_name: return ""
    clean_name = re.sub(r'\[.*?\]|\(.*?\)|\..*', '', clean_name).replace('부문', '').replace('원본', '').strip()
    
    # 1. Search for .docx in v8 first
    try:
        import docx
        docx_files = glob.glob(os.path.join(V8_DOCX_DIR, "**", f"*{clean_name}*.docx"), recursive=True)
        if docx_files:
            doc = docx.Document(docx_files[0])
            return "\n".join([para.text for para in doc.paragraphs])
    except Exception:
        pass

    # 2. Search PDF
    try:
        import pdfplumber
        pdf_files = glob.glob(os.path.join(PDF_DIR, "**", f"*{clean_name}*.pdf"), recursive=True)
        if pdf_files:
            with pdfplumber.open(pdf_files[0]) as pdf:
                return "\n".join(page.extract_text() or '' for page in pdf.pages[:5])
    except Exception:
        pass
        
    return ""

def migrate_to_v85():
    print("🚀 Starting V8.5 Migration (Building SQLAlchemy Database)...")
    
    # Do not drop existing candidates.db SQLite tables to preserve existing 1425 records
    # Create tables missing, but keep data
    Base.metadata.create_all(bind=engine)
    
    if not os.path.exists(CACHE_FILE):
        print(f"❌ Cache {CACHE_FILE} not found!")
        return

    with open(CACHE_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    db: Session = SessionLocal()
    success = 0
    fail = 0
    
    print(f"📦 Total candidates to migrate: {len(data)}")
    
    for i, c in enumerate(data):
        cid = c.get("id")
        if not cid: continue
        
        name_kr = c.get("name_kr") or c.get("name", "Unknown")
        email = c.get("email", "")
        phone = c.get("phone", "")
        
        email = email.strip() if email else None
        phone = phone.strip() if phone else None
        
        # Ingestion Strategy: Try to find raw_text from PDF. If it fails, fallback to 'summary'
        raw_text = extract_text_from_file(name_kr)
        if not raw_text or len(raw_text) < 50:
            raw_text = c.get("summary", "")
            
        if not raw_text:
            # Cannot store NULL in raw_text per schema
            raw_text = f"[NO_TEXT_FOUND] {name_kr}"
            
        # Create Hash
        doc_hash = hashlib.sha256(raw_text.encode('utf-8')).hexdigest()
        logic_hash = generate_logic_hash(raw_text, CURRENT_PROMPT_VERSION)
        
        try:
            # Upsert Candidate
            db_cand = Candidate(
                id=cid,
                name_kr=name_kr,
                email=email if email else None,
                phone=phone if phone else None,
                raw_text=raw_text,
                document_hash=doc_hash,
                is_parsed=True if c.get("parsed_career_json") else False,
                is_neo4j_synced=False,
                is_pinecone_synced=False
            )
            db.merge(db_cand)
            
            # Upsert ParsingCache
            # Instead of keeping just careers, we keep everything that UI needs in the Cache
            parsed_json_data = {
                "seniority": c.get("seniority", ""),
                "sector": c.get("sector", ""),
                "main_sectors": c.get("main_sectors", []),
                "profile_summary": c.get("profile_summary", ""), # To be populated by batch summary
                "careers": c.get("parsed_career_json", [])
            }
            
            db_cache = ParsingCache(
                candidate_id=cid,
                prompt_version=CURRENT_PROMPT_VERSION,
                logic_hash=logic_hash,
                parsed_json=json.dumps(parsed_json_data, ensure_ascii=False)
            )
            db.merge(db_cache)
            
            db.commit() # Save eagerly per row to isolate integrity errors
            success += 1
            if success % 50 == 0:
                print(f"  [Progress] {success}/{len(data)} migrated...")
                
        except Exception as e:
            print(f"❌ Error migrating {name_kr}: {e}")
            db.rollback()
            fail += 1
            
    db.commit()
    db.close()
    
    print(f"\n✨ V8.5 SQLite Migration Complete!")
    print(f"   - Success: {success}")
    print(f"   - Failed: {fail}")

if __name__ == "__main__":
    migrate_to_v85()
