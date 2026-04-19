import os

file_path = "backend/main.py"
with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

# 1. Add imports
imports_to_add = """
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

DB_PATH = os.path.join(ROOT_DIR, "candidates.db")

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

"""

if "import sqlite3" not in content:
    idx = content.find("app = FastAPI(")
    if idx != -1:
        content = content[:idx] + imports_to_add + "\n" + content[idx:]

# 2. Add Endpoints
endpoints_to_add = """

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

@app.post("/api/history")
def add_history(req: HistoryRequest, current_user: dict = Depends(get_current_user)):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO user_search_history (user_id, query) VALUES (?, ?)", (current_user["id"], req.query))
    
    # Keep only 50
    cursor.execute(\"""
        DELETE FROM user_search_history 
        WHERE id NOT IN (
            SELECT id FROM user_search_history 
            WHERE user_id = ? 
            ORDER BY created_at DESC 
            LIMIT 50
        ) AND user_id = ?
    \""", (current_user["id"], current_user["id"]))
    
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
    conn.close()
    
    # Neo4j & Pinecone caching simulation
    return {
        "total_candidates": total_candidates,
        "neo4j_edges": 52784,
        "pinecone_vectors": 15291,
        "avg_edges_per_candidate": 21.0
    }

@app.get("/api/admin/users")
def get_admin_users(current_user: dict = Depends(get_current_user)):
    if not current_user["is_admin"]:
        raise HTTPException(status_code=403, detail="Forbidden")
    
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    # Left join to get query count
    rows = conn.cursor().execute(\"""
    SELECT u.id, u.name, u.role, u.last_login, u.is_admin,
           (SELECT COUNT(*) FROM user_search_history h WHERE h.user_id = u.id) as query_count
    FROM users u
    \""").fetchall()
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

"""

if "/api/auth/login" not in content:
    # insert before @app.get("/api/health")
    idx = content.find("@app.get(\"/api/health\")")
    if idx != -1:
        content = content[:idx] + endpoints_to_add + "\n" + content[idx:]
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        print("Backend API endpoints injected successfully!")
    else:
        print("Could not find insertion point!")
else:
    print("Endpoints already present.")

