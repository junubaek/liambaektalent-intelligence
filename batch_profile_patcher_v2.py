import os
import json
import sqlite3
import re
import time
import google.generativeai as genai
from tqdm import tqdm
import pdfplumber
from docx import Document

# ── 1. 설정 ──────────────────────────
DB_PATH = r"C:\Users\cazam\Downloads\이력서자동분석검색시스템\candidates.db"
FOLDER_V8 = r"C:\Users\cazam\Downloads\02_resume_converted_v8"
FOLDER_PRE = r"C:\Users\cazam\Downloads\02_resume 전처리"
REPORT_FILE = "missing_files_report.json"

print("[Init] 설정 로딩 및 Gemini 모델 준비 중...")
with open("secrets.json", "r", encoding="utf-8") as f:
    secrets = json.load(f)
genai.configure(api_key=secrets.get("GEMINI_API_KEY", ""))

model = genai.GenerativeModel(
    'gemini-2.5-flash-lite',
    generation_config={"response_mime_type": "application/json"}
)

EXTRACTION_PROMPT = """
당신은 전문 헤드헌터 파서입니다. 이력서를 분석해 다음 JSON 스키마에 맞게 빈칸 없이 추출하세요.

[JSON 스키마]
{
  "birth_year": 정수 (예: 1985. 없으면 null. '85년생' 등에서 4자리 유추 가능),
  "education": [
    {
      "school": "학교명",
      "major": "전공",
      "degree": "학위 (학사/석사/박사 등)",
      "graduation_year": "졸업연도 (2010 등)"
    }
  ],
  "careers": [
    {
      "company": "회사명",
      "title": "직급/직무",
      "start_date": "입사 (YYYY-MM 형식)",
      "end_date": "퇴사 (YYYY-MM 형식, 재직중시 '현재')"
    }
  ]
}

[이력서 원문]
{raw_text}
"""

def extract_meta(filename_str):
    company, role = "", ""
    comp_match = re.search(r'\[(.*?)\]', filename_str)
    if comp_match: company = comp_match.group(1).strip()
    role_match = re.search(r'\((.*?)\)', filename_str)
    if role_match: role = role_match.group(1).strip()
    clean = re.sub(r'\[.*?\]|\(.*?\)|\..*', '', filename_str)
    clean = re.sub(r'부문|원본|최종|포트폴리오|이력서|합격|이력|Resume|CV', '', clean, flags=re.IGNORECASE)
    matches = re.findall(r'[가-힣]{2,4}', clean)
    stop_words = {'컨설팅','경력','신입','기획','개발','채용','운영','영업','전략','재무','회계','인사','총무','팀장','리더','매니저'}
    valid = [m for m in matches if m not in stop_words]
    name_kr = valid[-1] if valid else (matches[-1] if matches else clean.strip())
    return name_kr

def extract_phone(text):
    match = re.search(r'010[- .]?\d{4}[- .]?\d{4}', text)
    return match.group(0).replace(' ', '').replace('.', '').replace('-', '') if match else ""

def extract_email(text):
    match = re.search(r'[\w.-]+@[\w.-]+\.\w+', text)
    return match.group(0) if match else ""

def extract_text_natively(filepath):
    ext = filepath.rsplit(".", 1)[-1].lower()
    try:
        if ext == "pdf":
            with pdfplumber.open(filepath) as pdf:
                return "\n".join(p.extract_text() or "" for p in pdf.pages)
        elif ext in ("docx"):
            doc = Document(filepath)
            return "\n".join(p.text for p in doc.paragraphs)
    except Exception as e:
        return f"ERROR: {e}"
    return "UNSUPPORTED_EXT"

# ── 2. 매핑 로직 ───────────────────────
def run_mapping_and_patch():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    
    # DB 후보자 가져오기
    c.execute("SELECT id, name_kr, phone, email, birth_year FROM candidates")
    db_candidates = c.fetchall()
    
    # name_kr -> list of dicts
    db_map = {}
    for row in db_candidates:
        name = row['name_kr']
        db_map.setdefault(name, []).append(dict(row))
        
    print("[1] 실제 물리 파일 스캔 중...")
    all_files = {} # base_name -> filepath
    
    # 전처리 (PDF 등) 먼저 스캔
    if os.path.exists(FOLDER_PRE):
        for f in os.listdir(FOLDER_PRE):
            if f.endswith(('.pdf', '.docx', '.doc')):
                base = f.rsplit('.', 1)[0]
                all_files[base] = os.path.join(FOLDER_PRE, f)
                
    # V8 (깨끗한 docx) 우선 덮어쓰기
    if os.path.exists(FOLDER_V8):
        for f in os.listdir(FOLDER_V8):
            if f.endswith('.docx'):
                base = f.rsplit('.', 1)[0]
                all_files[base] = os.path.join(FOLDER_V8, f)
    
    print(f"총 {len(all_files)}개의 고유 분석 대상 파일 목록 확인 완료.")
    
    unmatched_files = []
    duplicate_merges = []
    db_to_file_map = {} # candidate_id -> (filepath, extracted_text)
    
    print("[2] 매핑 및 텍스트 파싱 진행 중...")
    for base_name, filepath in tqdm(all_files.items()):
        name_kr = extract_meta(base_name)
        text = extract_text_natively(filepath)
        
        if text.startswith("ERROR") or text == "UNSUPPORTED_EXT":
            unmatched_files.append({
                "file": base_name,
                "name_kr": name_kr,
                "reason": f"Text Extraction Failed: {text}"
            })
            continue
            
        f_phone = extract_phone(text)
        f_email = extract_email(text)
        
        possible_rows = db_map.get(name_kr, [])
        matched_row = None
        
        if len(possible_rows) == 1:
            matched_row = possible_rows[0]
        elif len(possible_rows) > 1:
            # 다중 매치 시 연락처나 이메일로 검색
            for row in possible_rows:
                db_p = (row['phone'] or '').replace('-', '').replace(' ','')
                if f_phone and db_p and f_phone in db_p:
                    matched_row = row
                    break
                if f_email and row['email'] and f_email.lower() == row['email'].lower():
                    matched_row = row
                    break
            # 못찾았으면 첫번째 걸로라도 임시 매핑 시도 (전화번호가 아예 둘 다 없을 수 있음)
            if not matched_row:
                matched_row = possible_rows[0]
        
        if matched_row:
            c_id = matched_row['id']
            # 중복 체크
            if c_id in db_to_file_map:
                duplicate_merges.append(f"A파일({db_to_file_map[c_id][0]})과 B파일({filepath})이 동일 인물({name_kr})로 판단되어 1명의 DB Row[{c_id}]로 병합됨.")
            else:
                db_to_file_map[c_id] = (filepath, text)
        else:
            unmatched_files.append({
                "file": base_name,
                "name_kr": name_kr,
                "extracted_phone": f_phone,
                "reason": "DB에 name_kr 매칭되는 행 없음"
            })
            
    # 리포트 저장
    report = {
        "total_files_scanned": len(all_files),
        "db_candidates_count": len(db_candidates),
        "successful_mapped_files (unique DB id)": len(db_to_file_map),
        "unmatched_files_count": len(unmatched_files),
        "duplicate_merges_count": len(duplicate_merges),
        "unmatched_list": unmatched_files,
        "duplicate_logs": duplicate_merges
    }
    with open(REPORT_FILE, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
        
    print(f"\n[안내] 매핑 리포트 저장 완료 ({REPORT_FILE})")
    print(f"매핑 성공: {len(db_to_file_map)}명 / 중복 병합: {len(duplicate_merges)}건 / 매칭 실패(고아): {len(unmatched_files)}건")
    
    # ── 3. Gemini API 호출 및 DB 패치 ─────────────────
    print("\n[3] V8.7 무결성 백필 시작... (DB 업데이트)")
    success_count = 0
    
    for candidate_id, (fp, clean_text) in tqdm(db_to_file_map.items()):
        # clean_text가 DB의 raw_text로 교체될 예정
        if len(clean_text) < 50:
            continue
            
        prompt = EXTRACTION_PROMPT.replace('{raw_text}', clean_text[:8000])
        
        try:
            # V8.7: 기존에 이미 birth_year가 채워져 있어도 API 안 돌리고 text만 교체하고 넘어갈수도 있지만
            # 전체 백필을 원하므로, birth_year 여부 상관없이 싹다 Gemini 추출!
            response = model.generate_content(prompt)
            result = json.loads(response.text)
            
            birth_year = result.get('birth_year')
            education_json = json.dumps(result.get('education', []), ensure_ascii=False)
            careers_json = json.dumps(result.get('careers', []), ensure_ascii=False)
            
            c.execute("""
                UPDATE candidates 
                SET raw_text = ?, birth_year = ?, education_json = ?, careers_json = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (clean_text, birth_year, education_json, careers_json, candidate_id))
            
            success_count += 1
            if success_count % 20 == 0:
                conn.commit()
                
            time.sleep(1.0) # API Limit 방지
            
        except Exception as e:
            # 실패 시에도 raw_text 교체는 진행 (깨끗한 텍스트로 보존)
            c.execute("UPDATE candidates SET raw_text = ? WHERE id = ?", (clean_text, candidate_id))
            conn.commit()
            # print(f"⚠️ API 파싱 에러 (ID {candidate_id}): {e}")
            
    conn.commit()
    conn.close()
    
    print(f"✅ 대규모 백필 작업 완료! (DB 추출 성공: {success_count}명)")

if __name__ == "__main__":
    run_mapping_and_patch()
