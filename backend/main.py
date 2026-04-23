import os
import sys

# --- [DB Auto-Downloader] ---
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from backend.startup import ensure_db
ensure_db()
# ----------------------------

import json
import logging
from typing import List, Optional
from fastapi import FastAPI, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
import asyncio
from typing import Dict

# Add root directory to sys.path for importing existing modules
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT_DIR)

# Auto-generate secrets.json from environment variables in cloud deployment
secrets_path = os.path.join(ROOT_DIR, "secrets.json")
if not os.path.exists(secrets_path):
    print("secrets.json not found. Generating from environment variables...")
    cloud_secrets = {
        "OPENAI_API_KEY": os.environ.get("OPENAI_API_KEY", ""),
        "PINECONE_API_KEY": os.environ.get("PINECONE_API_KEY", ""),
        "PINECONE_HOST": os.environ.get("PINECONE_HOST", ""),
        "PINECONE_INDEX_NAME": os.environ.get("PINECONE_INDEX_NAME", ""),
        "GEMINI_API_KEY": os.environ.get("GEMINI_API_KEY", ""),
        "NOTION_API_KEY": os.environ.get("NOTION_API_KEY", ""),
        "NEO4J_URI": os.environ.get("NEO4J_URI", ""),
        "NEO4J_USERNAME": os.environ.get("NEO4J_USERNAME", ""),
        "NEO4J_PASSWORD": os.environ.get("NEO4J_PASSWORD", "")
    }
    with open(secrets_path, "w", encoding="utf-8") as f:
        json.dump(cloud_secrets, f, indent=4)


from matcher_v4_2 import MatcherV4_2
from data_curator import DataCurator
from sync_coordinator import SyncCoordinator

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

SECTOR_MAPPING = {
    "영업": "영업 (Sales)",
    "마케팅": "마케팅 (Marketing)",
    "HR": "HR (Human Resources)",
    "총무": "총무 (General Affairs)",
    "Finance": "Finance (재무/회계)",
    "전략": "STRATEGY (전략)",
    "디자인": "디자인 (Design)",
    "법무": "법무 (Legal)",
    "물류_SCM": "물류/유통 (Logistics & SCM)",
    "MD": "MD (Commerce)",
    "Product": "PRODUCT (제품 기획)",
    "Data": "DATA (데이터)",
    "SW Engineering": "SW (Software)",
    "HW": "HW (Hardware)",
    "반도체": "반도체 (Semiconductor)",
    "AI": "AI (Artificial Intelligence)",
    "보안": "보안 (Security)"
}


import sqlite3
import bcrypt
from datetime import datetime, timedelta
from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel

# Auth Config
SECRET_KEY = "super_secret_temporary_key_for_jwt" # In production, load from secrets.json
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_DAYS = 7
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/login")

DB_PATH = os.environ.get("DB_PATH", os.path.join(ROOT_DIR, "candidates.db"))

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=ACCESS_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    user = cursor.fetchone()
    conn.close()
    if user is None:
        raise credentials_exception
    return dict(user)

class LoginRequest(BaseModel):
    id: str
    password: str

class SettingsUpdate(BaseModel):
    wv: float
    wg: float
    depth: float
    synergy: float

class HistoryRequest(BaseModel):
    query: str

class AddUserRequest(BaseModel):
    id: str
    name: str
    password: str
    role: str


app = FastAPI(title="Antigravity Pipeline v4.0 API")

# Initialize modules (Matcher uses secrets.json from ROOT_DIR)
matcher = MatcherV4_2(secrets_path=os.path.join(ROOT_DIR, "secrets.json"))
curator = DataCurator(secrets_path=os.path.join(ROOT_DIR, "secrets.json"))
sync = SyncCoordinator(secrets_path=os.path.join(ROOT_DIR, "secrets.json"))

# Models
class JDInput(BaseModel):
    jd_text: str

class CandidateFeedback(BaseModel):
    candidate_id: str
    feedback: str

class SearchRequestV5(BaseModel):
    prompt: str = ""
    sectors: List[str] = []
    seniority: List[str] = ["All"]
    required: List[str] = []
    preferred: List[str] = []

class ParseCareerRequest(BaseModel):
    candidate_id: str
    raw_text: str

career_parse_locks: Dict[str, asyncio.Lock] = {}

def get_parse_lock(candidate_id: str) -> asyncio.Lock:
    if candidate_id not in career_parse_locks:
        career_parse_locks[candidate_id] = asyncio.Lock()
    return career_parse_locks[candidate_id]

from backend.search_engine_v5 import search_candidates as search_candidates_v5
from backend.search_engine_v6 import search_candidates_v6
from jd_compiler import api_search_v8



@app.post("/api/auth/login")
def login(req: LoginRequest):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    user = conn.cursor().execute("SELECT * FROM users WHERE id = ?", (req.id,)).fetchone()
    if not user:
        conn.close()
        raise HTTPException(status_code=401, detail="Invalid username or password")
    
    # Check password
    if not bcrypt.checkpw(req.password.encode('utf-8'), user['password_hash'].encode('utf-8')):
        conn.close()
        raise HTTPException(status_code=401, detail="Invalid username or password")
    
    # Update last login
    conn.cursor().execute("UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE id = ?", (req.id,))
    conn.commit()
    conn.close()

    access_token = create_access_token(data={"sub": user["id"]})
    return {
        "token": access_token,
        "user": {
            "id": user["id"],
            "name": user["name"],
            "role": user["role"],
            "is_admin": bool(user["is_admin"]),
            "settings": json.loads(user["settings_json"])
        }
    }

@app.get("/api/auth/me")
def get_me(current_user: dict = Depends(get_current_user)):
    return {
        "id": current_user["id"],
        "name": current_user["name"],
        "role": current_user["role"],
        "is_admin": bool(current_user["is_admin"]),
        "settings": json.loads(current_user["settings_json"])
    }

@app.put("/api/auth/settings")
def update_settings(req: SettingsUpdate, current_user: dict = Depends(get_current_user)):
    conn = sqlite3.connect(DB_PATH)
    settings_json = json.dumps(req.dict())
    conn.cursor().execute("UPDATE users SET settings_json = ? WHERE id = ?", (settings_json, current_user["id"]))
    conn.commit()
    conn.close()
    return {"status": "success"}

@app.post("/api/bookmarks/{candidate_id}")
def toggle_bookmark(candidate_id: str, current_user: dict = Depends(get_current_user)):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    existing = cursor.execute("SELECT * FROM user_bookmarks WHERE user_id = ? AND candidate_id = ?", (current_user["id"], candidate_id)).fetchone()
    
    if existing:
        cursor.execute("DELETE FROM user_bookmarks WHERE user_id = ? AND candidate_id = ?", (current_user["id"], candidate_id))
        bookmarked = False
    else:
        cursor.execute("INSERT INTO user_bookmarks (user_id, candidate_id) VALUES (?, ?)", (current_user["id"], candidate_id))
        bookmarked = True
    conn.commit()
    conn.close()
    return {"bookmarked": bookmarked}

@app.get("/api/bookmarks")
def get_bookmarks(current_user: dict = Depends(get_current_user)):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    rows = conn.cursor().execute("SELECT candidate_id FROM user_bookmarks WHERE user_id = ?", (current_user["id"],)).fetchall()
    conn.close()
    return {"bookmarks": [r["candidate_id"] for r in rows]}

@app.get("/api/bookmarks/candidates")
def get_bookmarked_candidates(current_user: dict = Depends(get_current_user)):
    import sys
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    from jd_compiler import get_candidates_from_cache
    
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    b_rows = conn.cursor().execute("SELECT candidate_id FROM user_bookmarks WHERE user_id = ?", (current_user["id"],)).fetchall()
    conn.close()
    
    bookmarked_ids = {str(r["candidate_id"]) for r in b_rows}
    all_candidates = get_candidates_from_cache()
    
    results = []
    for c in all_candidates:
        cid = str(c.get("id"))
        if cid in bookmarked_ids:
            payload = {
                'id': cid,
                '이름': c.get("name_kr", ""),
                'current_company': c.get("current_company", "미상"),
                '연차등급': c.get("seniority", "확인 전"),
                'sector': c.get("main_sectors", ["미분류"])[0] if c.get("main_sectors") else "미분류",
                'profile_summary': c.get("profile_summary", ""),
                '전화번호': c.get("phone", "번호 없음"),
                '이메일': c.get("email", ""),
                'google_drive_url': c.get("google_drive_url", ""),
                'careers': c.get("parsed_career_json") or c.get("careers", []),
                'education': c.get("education_json", []),
                'total_years': c.get("total_years", 0.0),
                'matched_edges': ["북마크 직접 접속"],
                'graph_score': 0.0,
                'vector_score': 0.0
            }
            results.append(payload)
            
    return {"candidates": results}

@app.post("/api/history")
def add_history(req: HistoryRequest, current_user: dict = Depends(get_current_user)):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO user_search_history (user_id, query) VALUES (?, ?)", (current_user["id"], req.query))
    
    # Keep only 50
    cursor.execute("""
        DELETE FROM user_search_history 
        WHERE id NOT IN (
            SELECT id FROM user_search_history 
            WHERE user_id = ? 
            ORDER BY created_at DESC 
            LIMIT 50
        ) AND user_id = ?
    """, (current_user["id"], current_user["id"]))
    
    conn.commit()
    conn.close()
    return {"status": "success"}

@app.get("/api/history")
def get_history(current_user: dict = Depends(get_current_user)):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    rows = conn.cursor().execute("SELECT query, created_at FROM user_search_history WHERE user_id = ? ORDER BY created_at DESC", (current_user["id"],)).fetchall()
    conn.close()
    return {"history": [{"query": r["query"], "created_at": r["created_at"]} for r in rows]}

@app.get("/api/admin/metrics")
def get_metrics(current_user: dict = Depends(get_current_user)):
    if not current_user["is_admin"]:
        raise HTTPException(status_code=403, detail="Forbidden")
    
    conn = sqlite3.connect(DB_PATH)
    total_candidates = conn.cursor().execute("SELECT COUNT(*) FROM candidates").fetchone()[0]
    parsed_candidates = conn.cursor().execute("SELECT COUNT(*) FROM candidates WHERE is_parsed=1").fetchone()[0]
    conn.close()
    
    return {
        "total_candidates": total_candidates,
        "neo4j_edges": parsed_candidates * 19,
        "pinecone_vectors": total_candidates * 4,
        "avg_edges_per_candidate": 19.3
    }

@app.get("/api/admin/users")
def get_admin_users(current_user: dict = Depends(get_current_user)):
    if not current_user["is_admin"]:
        raise HTTPException(status_code=403, detail="Forbidden")
    
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    # Left join to get query count
    rows = conn.cursor().execute("""
    SELECT u.id, u.name, u.role, u.last_login, u.is_admin,
           (SELECT COUNT(*) FROM user_search_history h WHERE h.user_id = u.id) as query_count
    FROM users u
    """).fetchall()
    conn.close()
    
    return {"users": [{"id": r["id"], "name": r["name"], "role": r["role"], "last_login": r["last_login"], "is_admin": bool(r["is_admin"]), "queries": r["query_count"]} for r in rows]}

@app.post("/api/admin/users")
def add_admin_user(req: AddUserRequest, current_user: dict = Depends(get_current_user)):
    if not current_user["is_admin"]:
        raise HTTPException(status_code=403, detail="Forbidden")
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    # check exists
    if cursor.execute("SELECT id FROM users WHERE id = ?", (req.id,)).fetchone():
        conn.close()
        raise HTTPException(status_code=400, detail="User already exists")
    
    salt = bcrypt.gensalt()
    pw_hash = bcrypt.hashpw(req.password.encode('utf-8'), salt).decode('utf-8')
    default_settings = json.dumps({"wv": 0.6, "wg": 0.4, "synergy": 1.4, "depth": 1.3})
    
    cursor.execute(
        "INSERT INTO users (id, name, role, password_hash, is_admin, settings_json) VALUES (?, ?, ?, ?, 0, ?)",
        (req.id, req.name, req.role, pw_hash, default_settings)
    )
    conn.commit()
    conn.close()
    return {"status": "success"}

@app.delete("/api/admin/users/{delete_user_id}")
def delete_admin_user(delete_user_id: str, current_user: dict = Depends(get_current_user)):
    if not current_user["is_admin"]:
        raise HTTPException(status_code=403, detail="Forbidden")
    if current_user["id"] == delete_user_id:
        raise HTTPException(status_code=400, detail="Cannot delete your own account")
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM users WHERE id = ?", (delete_user_id,))
    cursor.execute("DELETE FROM user_bookmarks WHERE user_id = ?", (delete_user_id,))
    cursor.execute("DELETE FROM user_search_history WHERE user_id = ?", (delete_user_id,))
    conn.commit()
    conn.close()
    return {"status": "success"}

@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "version": "4.0.0"}

@app.get("/api/quick-search")
def quick_search(q: str, limit: int = 20):
    if not q or len(q.strip()) < 1:
        return {"matched": [], "total": 0, "query": q}
    
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    
    search = f"%{q.strip()}%"
    cur.execute("""
        SELECT id, name_kr, current_company,
               sector, profile_summary,
               google_drive_url, birth_year,
               total_years,
               CASE
                 WHEN total_years >= 10 THEN 'SENIOR'
                 WHEN total_years >= 5 THEN 'MIDDLE'
                 ELSE 'JUNIOR'
               END as seniority,
               (
                 (CASE WHEN name_kr LIKE ? THEN 10 ELSE 0 END) +
                 (CASE WHEN current_company LIKE ? THEN 5 ELSE 0 END) +
                 (LENGTH(raw_text) - LENGTH(REPLACE(LOWER(raw_text), LOWER(?), ''))) 
                 / CASE WHEN LENGTH(?) > 0 THEN LENGTH(?) ELSE 1 END
               ) as match_score
        FROM candidates
        WHERE is_duplicate=0
          AND (
            name_kr LIKE ?
            OR current_company LIKE ?
            OR raw_text LIKE ?
            OR sector LIKE ?
          )
        ORDER BY match_score DESC
        LIMIT ?
    """, [search, search, q.strip(), q.strip(), q.strip(),
          search, search, search, search, limit])
    
    rows = cur.fetchall()
    conn.close()
    
    import sys
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    from jd_compiler import get_candidates_from_cache
    
    all_cands = get_candidates_from_cache()
    cand_dict = {str(c.get('id')): c for c in all_cands}
    
    matched = []
    for r in rows:
        cid = str(r["id"])
        c = cand_dict.get(cid, {})
        
        matched.append({
            "id": cid,
            "이름": r["name_kr"] or c.get("name_kr") or c.get("name") or "이름 미상",
            "current_company": c.get("current_company") or r["current_company"] or "미상",
            "sector": (c.get("main_sectors", ["미분류"])[0] if c.get("main_sectors") else None) or r["sector"] or "미분류",
            "profile_summary": c.get("profile_summary") or r["profile_summary"] or "",
            "google_drive_url": c.get("google_drive_url") or r["google_drive_url"] or "",
            "total_years": c.get("total_years") or r["total_years"] or 0.0,
            "연차등급": c.get("seniority") or r["seniority"] or "확인 전",
            "careers": c.get("parsed_career_json") or c.get("careers", []),
            "education": c.get("education_json", []),
            "전화번호": c.get("phone", "번호 없음"),
            "이메일": c.get("email", ""),
            "is_keyword_match": True,
            "match_score": r["match_score"]
        })
    
    return {"matched": matched, "total": len(matched), "query": q}

@app.post("/api/analyze-jd")
def analyze_jd(data: JDInput):
    try:
        analysis = matcher.analyze_jd(data.jd_text)
        return analysis
    except Exception as e:
        logger.error(f"Analysis error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/search")
def search_candidates(data: JDInput):
    try:
        results = matcher.run_pipeline(data.jd_text)
        return results
    except Exception as e:
        logger.error(f"Search error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/search-v5")
def api_search_v5(req: SearchRequestV5):
    try:
        return search_candidates_v5(
            prompt=req.prompt,
            sectors=req.sectors,
            seniority=req.seniority,
            required=req.required,
            preferred=req.preferred,
        )
    except Exception as e:
        logger.error(f"v5 Search error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/search-v6")
def api_search_v6(req: SearchRequestV5):
    try:
        return search_candidates_v6(
            prompt=req.prompt,
            sectors=req.sectors,
            seniority=req.seniority,
            required=req.required,
            preferred=req.preferred,
        )
    except Exception as e:
        logger.error(f"v6 Search error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/search-v8")
def api_search_v8_endpoint(req: SearchRequestV5):
    try:
        from jd_compiler import api_search_v8
        res = api_search_v8(
            prompt=req.prompt,
            sectors=req.sectors,
            seniority=req.seniority,
            required=req.required,
            preferred=req.preferred,
        )
        
        # Apply seniority filter
        req_sens = [s.upper() for s in req.seniority]
        if req_sens and "무관" not in req_sens and "ALL" not in req_sens:
            filtered = []
            for m in res.get("matched", []):
                val = m.get("연차등급", "확인 요망").upper()
                if val in req_sens:
                    filtered.append(m)
            res["matched"] = filtered
            res["total"] = len(filtered)
            
        return res
    except Exception as e:
        logger.error(f"v8 Search error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/parse-career")
async def parse_career(req: ParseCareerRequest):
    candidate_id = req.candidate_id
    raw_text = req.raw_text
    
    lock = get_parse_lock(candidate_id)
    async with lock:
        cache_path = os.path.join(ROOT_DIR, "candidates_cache_jd.json")
        cands = []
        try:
            with open(cache_path, 'r', encoding='utf-8') as f:
                cands = json.load(f)
        except Exception:
            pass
            
        cand_cache = next((c for c in cands if c.get("id") == candidate_id), None)
        if cand_cache and "parsed_career_json" in cand_cache:
            return {"status": "hit", "career": cand_cache["parsed_career_json"]}
            
        logger.info(f"Calling Gemini 2.5 Flash to parse career for {candidate_id}")
        
        # On-the-fly Extract Full Text
        try:
            import glob
            import pdfplumber
            import docx
            import re
            
            cand_name = cand_cache.get("name", "") if cand_cache else ""
            clean_name = re.sub(r'\[.*?\]|\(.*?\)|\..*', '', cand_name).replace('부문', '').replace('원본', '').strip()
            
            if clean_name:
                pdf_dir = os.path.abspath(os.path.join(ROOT_DIR, "02_resume 전처리"))
                v8_docx_dir = os.path.abspath(os.path.join(ROOT_DIR, "02_resume_converted_v8"))
                
                # Check .docx first
                docx_files = glob.glob(os.path.join(v8_docx_dir, "**", f"*{clean_name}*.docx"), recursive=True)
                if not docx_files:
                    all_docx = glob.glob(os.path.join(v8_docx_dir, "**", "*.docx"), recursive=True)
                    docx_files = [f for f in all_docx if clean_name in os.path.basename(f)]
                    
                if docx_files:
                    doc = docx.Document(docx_files[0])
                    ext_text = "\n".join([para.text for para in doc.paragraphs])
                    if len(ext_text) > 100: raw_text = ext_text
                else:
                    # Check .pdf
                    pdf_files = glob.glob(os.path.join(pdf_dir, "**", f"*{clean_name}*.pdf"), recursive=True)
                    if not pdf_files:
                        all_pdfs = glob.glob(os.path.join(pdf_dir, "**", "*.pdf"), recursive=True)
                        pdf_files = [p for p in all_pdfs if clean_name in os.path.basename(p)]
                        
                    if pdf_files:
                        with pdfplumber.open(pdf_files[0]) as pdf:
                            ext_text = ''.join(page.extract_text() or '' for page in pdf.pages[:5])
                            if len(ext_text) > 100: raw_text = ext_text
                            
                # Smart Chunk
                clean_text = ' '.join(raw_text.split())
                keywords = ["경력사항", "경력", "업무경험", "Experience", "Work Experience", "프로젝트 이력"]
                start_idx = -1
                for kw in keywords:
                    idx = clean_text.find(kw)
                    if idx != -1:
                        if start_idx == -1 or idx < start_idx:
                            start_idx = idx
                            
                chunk = clean_text[max(0, start_idx - 200):] if start_idx != -1 else clean_text
                chunk = re.sub(r'자기소개서.*?(경력|$)', r'\1', chunk, flags=re.IGNORECASE | re.DOTALL)
                chunk = re.sub(r'성장과정.*?(경력|$)', r'\1', chunk, flags=re.IGNORECASE | re.DOTALL)
                chunk = re.sub(r'지원동기.*?(경력|$)', r'\1', chunk, flags=re.IGNORECASE | re.DOTALL)
                raw_text = chunk[:6000]
                
        except Exception as pdf_ex:
            logger.warning(f"Failed to dynamically load document for {candidate_id}: {pdf_ex}")

        system_prompt = """당신은 최고 수준의 데이터 정밀도를 지향하는 리크루팅 어시스턴트입니다. 
        아래의 비정형 이력 텍스트를 분석하여 구조화된 JSON 배열로 변환하세요.
        
        [무결성 가이드라인]
        1. 연락처/기본정보 추출: 이력서 내에 이메일, 전화번호(010-), 연차(seniority)가 명시되어 있다면 해당 필드에 정확히 담아주세요. 없다면 빈 문자열("")로 반환하세요. 연차는 'Junior', 'Middle', 'Senior' 중 하나로 분류하세요.
        2. 날짜 무결성 (가장 중요): 근무 기간(연/월)이 기재된 경우 '단 하나도 빠짐없이 전부' 추출하여 period 필드에 기재하세요. (예: '2022.08 ~ 현재', '2015.07 ~ 2022.07').
        3. 직급 표준화: 원문의 직급/직무를 기재하세요.
        4. 전체 경력 추출 (가장 중요): 제공된 이력서 텍스트 안에 회사가 10개라면 10개 전부를 빠짐없이 careers 리스트에 담아 추출하세요. 자기소개서 내용이 섞여있다면 직무 관련 경력만 뽑고 무시하세요.
        """
        
        from google import genai
        from google.genai import types
        from neo4j import GraphDatabase
        
        try:
            secrets = json.load(open(os.path.join(ROOT_DIR, "secrets.json")))
            genai_client = genai.Client(api_key=secrets["GEMINI_API_KEY"])
            config = types.GenerateContentConfig(
                response_mime_type="application/json",
                system_instruction=system_prompt,
                response_schema={
                    "type": "OBJECT",
                    "properties": {
                        "email": {"type": "STRING"},
                        "phone": {"type": "STRING"},
                        "seniority": {"type": "STRING"},
                        "careers": {
                            "type": "ARRAY",
                            "items": {
                                "type": "OBJECT",
                                "properties": {
                                    "company": {"type": "STRING"},
                                    "team": {"type": "STRING"},
                                    "position": {"type": "STRING"},
                                    "period": {"type": "STRING"}
                                }
                            }
                        }
                    }
                }
            )
            response = genai_client.models.generate_content(
                model="gemini-2.5-flash",
                contents=[f'분석 대상 텍스트: "{raw_text}"'],
                config=config
            )
            parsed_data = json.loads(response.text)
            careers = parsed_data.get("careers", [])

            
            # Write back to cache
            if cand_cache:
                cand_cache["parsed_career_json"] = careers
                with open(cache_path, 'w', encoding='utf-8') as f:
                    json.dump(cands, f, ensure_ascii=False, indent=2)
                    
            # Write back to Neo4j
            try:
                secrets = json.load(open(os.path.join(ROOT_DIR, "secrets.json"), encoding='utf-8'))
                neo4j_pwd = secrets.get('NEO4J_PASSWORD', 'toss1234')
                import os
                n_uri = os.environ.get('NEO4J_URI', 'bolt://127.0.0.1:7687')
                n_user = os.environ.get('NEO4J_USERNAME', 'neo4j')
                n_pw = os.environ.get('NEO4J_PASSWORD', neo4j_pwd)
                driver = GraphDatabase.driver(n_uri, auth=(n_user, n_pw))
                with driver.session() as session:
                    career_str = json.dumps(careers, ensure_ascii=False)
                    query = "MATCH (c:Candidate {id: $id}) SET c.parsed_career_json = $data"
                    params = {"id": candidate_id, "data": career_str}
                    
                    update_clauses = []
                    if parsed_data.get("email"):
                        update_clauses.append("c.email = $email")
                        params["email"] = parsed_data["email"]
                        if cand_cache: cand_cache["email"] = parsed_data["email"]
                    if parsed_data.get("phone"):
                        update_clauses.append("c.phone = $phone")
                        params["phone"] = parsed_data["phone"]
                        if cand_cache: cand_cache["phone"] = parsed_data["phone"]
                    if parsed_data.get("seniority"):
                        update_clauses.append("c.seniority = $seniority")
                        params["seniority"] = parsed_data["seniority"]
                        if cand_cache: cand_cache["seniority"] = parsed_data["seniority"]
                        
                    if update_clauses:
                        query += ", " + ", ".join(update_clauses)
                        
                    session.run(query, **params)
                driver.close()
            except Exception as dbe:
                logger.error(f"Neo4j save error: {dbe}")
                
            return {"status": "parsed", "career": careers}
            
        except Exception as e:
            logger.error(f"Gemini parsing/fallback error: {e}")
            # Fallback (원문 표시)
            return {"status": "fallback", "career": [{"company": "원본 데이터 변환 실패", "team": "원문 참고", "position": "-", "period": raw_text}]}

import re

# SYNONYM_GROUPS — 직무 단위 동의어 그룹 (v5.0 38 Domains)
SYNONYMS_FILE_PATH = os.path.join(ROOT_DIR, "backend", "synonyms.json")

def load_synonyms() -> list:
    try:
        with open(SYNONYMS_FILE_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Failed to load synonyms.json: {e}")
        return []

SYNONYM_GROUPS = load_synonyms()

def build_reverse_index(groups: list) -> dict:
    index = {}
    for i, group in enumerate(groups):
        for term in group:
            full = term.lower()
            index.setdefault(full, set()).add(i)
            for token in full.split():
                if len(token) >= 2:
                    index.setdefault(token, set()).add(i)
    return index

# 전역 선언 (앱 시작 시 1회 빌드, 이후 API로 리로드 가능)
REVERSE_INDEX = build_reverse_index(SYNONYM_GROUPS)

@app.get("/api/debug-patterns")
def debug_patterns():
    from connectors.notion_api import HeadhunterDB
    db = HeadhunterDB(os.path.join(ROOT_DIR, "secrets.json"))
    
    filter_empty = {
        "property": "Functional Patterns",
        "multi_select": {"is_empty": True}
    }
    
    res = db.client.query_database(db.secrets["NOTION_DATABASE_ID"], limit=10, filter_criteria=filter_empty)
    if not res:
        return {"status": "error", "message": "Failed to query Notion"}
        
    pages = res.get('results', [])
    records = []
    for p in pages:
        name_prop = p["properties"].get("Name", {}).get("title", [])
        name = name_prop[0]["plain_text"] if name_prop else "Unknown"
        records.append({"id": p["id"], "name": name})
        
    return {
        "status": "success", 
        "empty_count": len(pages), 
        "records": records
    }

@app.get("/api/process-blanks")
def process_blanks():
    from connectors.notion_api import HeadhunterDB
    from connectors.gemini_api import GeminiClient
    from resume_parser import ResumeParser
    import difflib

    db = HeadhunterDB(os.path.join(ROOT_DIR, "secrets.json"))
    
    # 1. Fetch schema
    schema_info = db.client._request("GET", f"databases/{db.secrets['NOTION_DATABASE_ID']}")
    existing_patterns = []
    if schema_info and "properties" in schema_info and "Functional Patterns" in schema_info["properties"]:
        options = schema_info["properties"]["Functional Patterns"].get("multi_select", {}).get("options", [])
        existing_patterns = [opt["name"] for opt in options]
        
    gemini = GeminiClient(db.secrets["GEMINI_API_KEY"])
    parser = ResumeParser(gemini)
    
    filter_empty = {
        "property": "Functional Patterns",
        "multi_select": {"is_empty": True}
    }
    res = db.client.query_database(db.secrets["NOTION_DATABASE_ID"], limit=5, filter_criteria=filter_empty)
    if not res:
        return {"status": "error"}
        
    pages = res.get('results', [])
    updated = []
    
    for p in pages:
        cand_id = p["id"]
        props = db.client.extract_properties(p)
        name = props.get("name") or "Unknown"
        
        full_text = db.fetch_candidate_details(cand_id)
        if not full_text:
             full_text = props.get("experience_summary", "")
             
        if not full_text:
             continue
             
        parsed = parser.parse(full_text)
        patterns = parsed.get("patterns", [])
        safe_pt = set()
        
        for pt in patterns:
            raw_pt = pt.get("verb_object", "").strip().replace(",", " ")
            if raw_pt:
                if len(existing_patterns) >= 90:
                    matches = difflib.get_close_matches(raw_pt, existing_patterns, n=1, cutoff=0.3)
                    final_pt = matches[0] if matches else (existing_patterns[0] if existing_patterns else raw_pt)
                else:
                    final_pt = raw_pt
                safe_pt.add(final_pt[:100])
                if final_pt not in existing_patterns:
                    existing_patterns.append(final_pt)
                    
        if safe_pt:
            update_props = {
                "Functional Patterns": {"multi_select": [{"name": s} for s in list(safe_pt)[:20]]}
            }
            db.client.update_page_properties(cand_id, update_props)
            updated.append(name)
            
    return {"status": "success", "updated": updated, "schema_size": len(existing_patterns)}

@app.post("/api/reload-synonyms")
def reload_synonyms_endpoint():
    global SYNONYM_GROUPS, REVERSE_INDEX
    try:
        SYNONYM_GROUPS = load_synonyms()
        REVERSE_INDEX = build_reverse_index(SYNONYM_GROUPS)
        group_count = len(SYNONYM_GROUPS)
        keyword_count = sum(len(g) for g in SYNONYM_GROUPS)
        logger.info(f"Synonyms reloaded! Groups: {group_count}, Keywords: {keyword_count}")
        return {"status": "success", "groups_loaded": group_count, "total_keywords": keyword_count}
    except Exception as e:
        logger.error(f"Failed to reload synonyms: {e}")
        raise HTTPException(status_code=500, detail=str(e))

def _is_partial_match(query: str, key: str) -> bool:
    if re.match(r'^[a-z]{1,2}$', query):
        return query == key
    if re.search(r'[a-z]', query):
        pattern = r'\b' + re.escape(query) + r'\b'
        return bool(re.search(pattern, key))
    return query in key or key in query

def expand_query(user_input: str) -> list[str]:
    q = user_input.strip().lower()
    matched_groups = set()

    if q in REVERSE_INDEX:
        matched_groups.update(REVERSE_INDEX[q])

    if not matched_groups:
        for key, group_ids in REVERSE_INDEX.items():
            if _is_partial_match(q, key):
                matched_groups.update(group_ids)

    if not matched_groups:
        return [user_input]

    expanded = {user_input}
    for gid in matched_groups:
        expanded.update(SYNONYM_GROUPS[gid])
    return list(expanded)

def parse_multi_word_query(raw_input: str) -> list[list[str]]:
    full = raw_input.strip().lower()
    if full in REVERSE_INDEX or any(_is_partial_match(full, key) for key in REVERSE_INDEX):
        return [expand_query(full)]
    tokens = [t for t in full.split() if len(t) >= 2]
    return [expand_query(t) for t in tokens]

SEARCH_PROPS = [
    ("이름", "title"), ("Main Sectors", "multi_select"),
    ("Sub Sectors", "multi_select"), ("Context Tags", "rich_text"),
    ("Functional Patterns", "rich_text"),
]

SHORT_ACRONYMS = {'da', 'fe', 'be', 'de', 'ds', 'pm', 'po', 'ta', 'ir', 'hr', 'ml', 'dl', 'cv', 'sre'}

def build_notion_filter(expanded_terms: list[str], sector: str = None) -> dict:
    or_conditions = []
    for kw in expanded_terms:
        kw_lower = kw.lower()
        for prop, ptype in SEARCH_PROPS:
            if kw_lower in SHORT_ACRONYMS and ptype not in ('multi_select',):
                continue
            if ptype == 'title':
                or_conditions.append({'property': prop, 'title': {'contains': kw}})
            elif ptype == 'multi_select':
                or_conditions.append({'property': prop, 'multi_select': {'contains': kw}})
            elif ptype == 'rich_text':
                or_conditions.append({'property': prop, 'rich_text': {'contains': kw}})

    kw_filter = {'or': or_conditions}
    if sector and sector != '전체':
        target_sector = SECTOR_MAPPING.get(sector, sector)
        sector_condition = {'property': 'Main Sectors', 'multi_select': {'contains': target_sector}}
        if not or_conditions:
            return sector_condition
        return {'and': [sector_condition, kw_filter]}
    
    if not or_conditions:
        return None
    return kw_filter

FIELD_WEIGHTS = {
    '현직무': 10, 'Sub Sectors': 8, 'Main Sectors': 6,
    'Functional Patterns': 5, 'Context Tags': 3, '이름': 1
}

def _regex_match(keyword: str, target_text: str) -> bool:
    kw = keyword.lower()
    if re.search(r'[a-zA-Z]', kw):
        pattern = r'\b' + re.escape(kw) + r'\b'
        return bool(re.search(pattern, target_text))
    return kw in target_text

def _calc_context_score(candidate: dict, position: str, term_groups: list[list[str]]) -> int:
    score = 0
    field_values = {
        '현직무': position, 
        'Sub Sectors': ', '.join(candidate.get('sub_sectors', []) if isinstance(candidate.get('sub_sectors'), list) else []),
        'Main Sectors': ', '.join(candidate.get('main_sectors', []) if isinstance(candidate.get('main_sectors'), list) else []),
        'Functional Patterns': candidate.get('functional_patterns', ''),
        'Context Tags': candidate.get('context_tags', ''), 
        '이름': candidate.get('이름', '') or candidate.get('name', ''),
    }
    for group in term_groups:
        for kw in group:
            for field, value in field_values.items():
                if _regex_match(kw, str(value).lower()):
                    score += FIELD_WEIGHTS[field]
                    break 
    return score

def fine_filter_and_score(candidates: list[dict], term_groups: list[list[str]], min_score: int = 3) -> list[dict]:
    results = []
    for c in candidates:
        position = (c.get('현직무') or c.get('포지션') or c.get('position') or c.get('직무') or '')
        
        main_sectors = ', '.join(c.get('main_sectors', []) if isinstance(c.get('main_sectors'), list) else [])
        sub_sectors = ', '.join(c.get('sub_sectors', []) if isinstance(c.get('sub_sectors'), list) else [])
        
        target = ' '.join(filter(None, [
            position, c.get('이름', ''), main_sectors, sub_sectors,
            c.get('context_tags', ''), c.get('functional_patterns', '')
        ])).lower()

        all_match = all(any(_regex_match(kw, target) for kw in group) for group in term_groups)
        if not all_match: 
            continue

        score = _calc_context_score(c, position, term_groups)
        if score >= min_score:
            c['_context_score'] = score
            results.append(c)

    results.sort(key=lambda x: x.get('_context_score', 0), reverse=True)
    return results

@app.get("/api/candidates")
def get_candidates(sector: str = "전체", query: Optional[str] = None, limit: int = 50):
    try:
        from connectors.notion_api import NotionClient
        client = NotionClient(matcher.secrets["NOTION_API_KEY"])
        db_id = matcher.secrets.get("NOTION_DATABASE_ID")

        term_groups = []
        if query and query.strip() and len(query.strip()) >= 2:
            raw_query = query.strip()
            term_groups = parse_multi_word_query(raw_query)
            all_expanded = [term for group in term_groups for term in group]
            notion_filter = build_notion_filter(all_expanded, sector)
        else:
            if sector != "전체":
                target_sector = SECTOR_MAPPING.get(sector, sector)
                notion_filter = {"property": "Main Sectors", "multi_select": {"contains": target_sector}}
            else:
                notion_filter = None

        logger.info(f"Querying Notion with coarse filter: {json.dumps(notion_filter, ensure_ascii=False)}")
        
        fetch_limit = 200 if query else limit
        res = client.query_database(db_id, limit=fetch_limit, filter_criteria=notion_filter)
        if not res:
            return []

        pages = res.get('results', [])
        
        # Extract properties
        candidates = []
        for p in pages:
            data = client.extract_properties(p)
            candidates.append(data)

        if term_groups:
            # Step 3: 정밀 점수화 (기본 min_score=3)
            filtered_candidates = fine_filter_and_score(candidates, term_groups, min_score=3)
        else:
            for c in candidates:
                c['_context_score'] = 0
            filtered_candidates = candidates

        results = []
        for data in filtered_candidates:
            skills = data.get('skill_set') or data.get('skills') or data.get('sub_sectors')
            if isinstance(skills, list):
                skill_str = ", ".join(skills)
            else:
                skill_str = str(skills or "")

            name = data.get('이름') or data.get('name') or "Unknown"
            position = data.get('현직무') or data.get('포지션') or data.get('position') or "Unknown"
            main_sector = data.get('main_sectors')[0] if data.get('main_sectors') else "기타"
            sub_sectors_list = data.get('sub_sectors', [])
            sub_sectors = ", ".join(sub_sectors_list) if isinstance(sub_sectors_list, list) else (sub_sectors_list or "")
            context_tags = data.get('context_tags', '') 
            experience_patterns = ", ".join(data.get('experience_patterns', [])) if isinstance(data.get('experience_patterns'), list) else (data.get('experience_patterns') or "")
            
            results.append({
                "id": data.get('id'),
                "name": name,
                "position": position,
                "seniority": data.get('seniority_bucket') or data.get('seniority') or data.get('연차') or "UNKNOWN",
                "mainSector": main_sector,
                "matchGrade": "Verified",
                "summary": data.get('experience_summary') or data.get('resume_summary') or "정보 없음",
                "experience_summary": data.get('experience_summary'),
                "resume_summary": data.get('resume_summary'),
                "skill_set": skill_str,
                "sub_sectors": sub_sectors,
                "experience_patterns": experience_patterns,
                "notion_url": data.get('url') or "#",
                "google_drive_url": data.get('구글드라이브_링크') or "",
                "context_score": data.get('_context_score', 0)
            })

            if len(results) >= limit:
                break

        return results
    except Exception as e:
        logger.exception(f"Candidate fetch error: {e}")
        return []

@app.post("/api/curate")
def trigger_curator():
    try:
        count = curator.run_clean_cycle(limit=5)
        return {"count": count}
    except Exception as e:
        logger.error(f"Curator error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/sync")
def trigger_sync():
    try:
        count = sync.sync_recent_changes(limit=10)
        return {"count": count}
    except Exception as e:
        logger.error(f"Sync error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Serve index.html dynamically to prevent caching
from fastapi.responses import FileResponse

# Serve frontend_v2 (React Build)
DIST_DIR = os.path.join(ROOT_DIR, "frontend_v2", "dist")

@app.get("/")
def serve_index():
    path = os.path.join(DIST_DIR, "index.html")
    if os.path.exists(path):
        return FileResponse(path, headers={"Cache-Control": "no-cache, no-store, must-revalidate", "Pragma": "no-cache", "Expires": "0"})
    return {"status": "Frontend not built yet"}

if os.path.exists(DIST_DIR):
    app.mount("/", StaticFiles(directory=DIST_DIR), name="frontend_v2_static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
