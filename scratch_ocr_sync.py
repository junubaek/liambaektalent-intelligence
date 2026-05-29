import json
import sqlite3
import sys
import time
import os
import google.generativeai as genai
from incremental_ingest_v10 import MEGA_PROMPT, calculate_career_stats
from neo4j import GraphDatabase
import win32com.client

sys.stdout.reconfigure(encoding='utf-8')

# secrets.json에서 API 키 로드
secrets_path = r"C:\Users\cazam\Downloads\이력서자동분석검색시스템\secrets.json"
with open(secrets_path, "r", encoding="utf-8") as f:
    secrets = json.load(f)

genai.configure(api_key=secrets["GEMINI_API_KEY"])
model = genai.GenerativeModel("gemini-2.5-flash")

n_uri = secrets.get("NEO4J_URI")
n_user = secrets.get("NEO4J_USERNAME")
n_pw = secrets.get("NEO4J_PASSWORD")
driver = GraphDatabase.driver(n_uri, auth=(n_user, n_pw))

db_path = r"C:\Users\cazam\Downloads\이력서자동분석검색시스템\candidates.db"
temp_pdf_dir = r"C:\Users\cazam\Downloads\이력서자동분석검색시스템\reparsing_temp"
os.makedirs(temp_pdf_dir, exist_ok=True)

conn = sqlite3.connect(db_path)
cur = conn.cursor()

# 남은 이미지/깨진 PDF/DOCX 대상 조회 (raw_text가 없거나 100자 미만인 경우)
cur.execute('''
    SELECT id, name_kr, google_drive_url, sector
    FROM candidates
    WHERE raw_text IS NULL OR length(raw_text) < 100
''')
rows = cur.fetchall()
conn.close()

print(f"Synchronous OCR Purification Target: {len(rows)} candidates")

dir_raw = r"C:\Users\cazam\Downloads\02_resume 전처리"
dir_conv = r"C:\Users\cazam\Downloads\02_resume_converted_v8"

def find_candidate_file(name_kr):
    clean = name_kr.split('(')[0].strip()
    raw_files = [f for f in os.listdir(dir_raw) if clean in f] if os.path.exists(dir_raw) else []
    conv_files = [f for f in os.listdir(dir_conv) if clean in f] if os.path.exists(dir_conv) else []
    
    # 1. PDF
    pdf_files = [f for f in raw_files if f.lower().endswith('.pdf')]
    if pdf_files:
        return os.path.join(dir_raw, pdf_files[0]), 'application/pdf', False
        
    # 2. DOCX (Raw)
    docx_files = [f for f in raw_files if f.lower().endswith('.docx')]
    if docx_files:
        return os.path.join(dir_raw, docx_files[0]), 'application/vnd.openxmlformats-officedocument.wordprocessingml.document', True
        
    # 3. Converted DOCX
    conv_docx = [f for f in conv_files if f.lower().endswith('.docx')]
    if conv_docx:
        return os.path.join(dir_conv, conv_docx[0]), 'application/vnd.openxmlformats-officedocument.wordprocessingml.document', True
        
    # 4. Raw DOC
    doc_files = [f for f in raw_files if f.lower().endswith('.doc')]
    if doc_files:
        return os.path.join(dir_raw, doc_files[0]), 'application/msword', True
        
    return None, None, False

# COM Word 준비
word = win32com.client.Dispatch("Word.Application")
word.Visible = False

for idx, r in enumerate(rows, 1):
    cid, name_kr, gdrive_url, old_sector = r
    filepath, mime_type, needs_conversion = find_candidate_file(name_kr)
    
    if not filepath:
        print(f"[{idx}/{len(rows)}] File not found locally for {name_kr}")
        continue
        
    pdf_path = filepath
    
    # PDF 변환이 필요한 경우
    if needs_conversion:
        temp_pdf_path = os.path.join(temp_pdf_dir, f"{name_kr}_{cid[:8]}.pdf")
        print(f"[{idx}/{len(rows)}] [Convert] {os.path.basename(filepath)} -> {os.path.basename(temp_pdf_path)}")
        try:
            doc = word.Documents.Open(os.path.abspath(filepath))
            time.sleep(0.5)
            doc.SaveAs(os.path.abspath(temp_pdf_path), FileFormat=17) # 17 is wdFormatPDF
            doc.Close()
            time.sleep(0.5)
            pdf_path = temp_pdf_path
        except Exception as e:
            print(f"[{idx}/{len(rows)}] [!] Convert Failed: {e}")
            continue
            
    # OCR 수행
    print(f"[{idx}/{len(rows)}] [OCR] {name_kr} -> {os.path.basename(pdf_path)}")
    raw_text = ""
    try:
        uploaded_file = genai.upload_file(path=pdf_path, mime_type='application/pdf')
        time.sleep(2)
        ocr_prompt = "이 스캔/이미지 기반의 이력서 PDF 파일의 모든 텍스트 내용을 누락이나 오타 없이 완벽하게 한글/영문 텍스트로 그대로 추출해주세요."
        response = model.generate_content([uploaded_file, ocr_prompt])
        raw_text = response.text.strip()
        try: uploaded_file.delete()
        except: pass
    except Exception as e:
        print(f"[{idx}/{len(rows)}] [!] OCR Failed: {e}")
        if needs_conversion and os.path.exists(pdf_path): os.remove(pdf_path)
        continue
        
    if not raw_text or len(raw_text) < 50:
        print(f"[{idx}/{len(rows)}] [!] OCR too short: {len(raw_text) if raw_text else 0}")
        if needs_conversion and os.path.exists(pdf_path): os.remove(pdf_path)
        continue
        
    # 구조화 파싱 수행
    parsed = None
    for attempt in range(3):
        try:
            prompt = MEGA_PROMPT.replace("{text}", f"[파일명: {name_kr}]\n\n" + raw_text[:6000])
            res = model.generate_content(prompt)
            raw = res.text.replace("```json", "").replace("```", "").strip()
            parsed = json.loads(raw)
            break
        except Exception as e:
            time.sleep(1.5)
            
    if not parsed:
        parsed_data = {
            "sector": old_sector, "summary": "", "careers": [], "edu": [],
            "current_company": "", "total_years": 0.0, "neo4j_edges": []
        }
    else:
        sector = parsed.get("sector", old_sector)
        summary = parsed.get("summary", "")
        careers = parsed.get("careers_json", [])
        edu = parsed.get("education_json", [])
        neo4j_edges = parsed.get("neo4j_edges", [])
        current_company, total_years = calculate_career_stats(careers)
        parsed_data = {
            "sector": sector, "summary": summary, "careers": careers, "edu": edu,
            "current_company": current_company, "total_years": total_years, "neo4j_edges": neo4j_edges
        }
        
    # SQLite 단일 업데이트 및 바로 커밋!
    try:
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()
        cur.execute('''
            UPDATE candidates 
            SET raw_text = ?, careers_json = ?, education_json = ?, profile_summary = ?, sector = ?, total_years = ?, current_company = ?, is_parsed = 1
            WHERE id = ?
        ''', (
            raw_text,
            json.dumps(parsed_data["careers"], ensure_ascii=False),
            json.dumps(parsed_data["edu"], ensure_ascii=False),
            parsed_data["summary"],
            parsed_data["sector"],
            parsed_data["total_years"],
            parsed_data["current_company"],
            cid
        ))
        conn.commit()
        affected = cur.rowcount
        conn.close()
        print(f"[{idx}/{len(rows)}] [SQLite Success] Rows Affected: {affected}")
    except Exception as e:
        print(f"[{idx}/{len(rows)}] [!] SQLite Update Failed: {e}")
        
    # Neo4j 그래프 업데이트
    try:
        with driver.session() as session:
            session.run("""
                MERGE (c:Candidate {id: $id})
                SET c.name = $name_kr, c.current_company = $current_company,
                    c.profile_summary = $summary, c.total_years = $total_years, c.sector = $sector
            """, id=cid, name_kr=name_kr, current_company=parsed_data["current_company"], summary=parsed_data["summary"], total_years=parsed_data["total_years"], sector=parsed_data["sector"])
            
            for edge in parsed_data["neo4j_edges"]:
                act, skill = edge.get("action", ""), edge.get("skill", "")
                conf = float(edge.get("confidence", 0.5))
                ev = edge.get("evidence_span", "")
                if act and skill:
                    session.run(f"""
                        MERGE (c:Candidate {{id: $id}})
                        MERGE (s:Skill {{name: $skill}})
                        MERGE (c)-[r:{act}]->(s)
                        SET r.confidence = $conf, r.evidence_span = $ev, r.source = 'ocr_purify_sync'
                    """, id=cid, skill=skill, conf=conf, ev=ev)
        print(f"[{idx}/{len(rows)}] [Neo4j Success] Candidate & skill edges updated.")
    except Exception as e:
        print(f"[{idx}/{len(rows)}] [!] Neo4j Update Failed: {e}")
        
    # 임시 파일 삭제
    if needs_conversion and os.path.exists(pdf_path):
        try: os.remove(pdf_path)
        except: pass

try: word.Quit()
except: pass

driver.close()
print("\nSynchronous OCR Purification Complete!")
