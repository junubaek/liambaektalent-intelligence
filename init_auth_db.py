import sqlite3
import os
import json
import logging
import bcrypt

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

DB_PATH = "candidates.db"

def get_password_hash(password):
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    logger.info("Creating users table...")
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
      id TEXT PRIMARY KEY,
      name TEXT NOT NULL,
      role TEXT DEFAULT 'user',
      password_hash TEXT NOT NULL,
      is_admin INTEGER DEFAULT 0,
      settings_json TEXT DEFAULT '{}',
      created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
      last_login DATETIME
    )
    """)

    logger.info("Creating user_bookmarks table...")
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS user_bookmarks (
      user_id TEXT,
      candidate_id TEXT,
      created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
      PRIMARY KEY (user_id, candidate_id)
    )
    """)

    logger.info("Creating user_search_history table...")
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS user_search_history (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      user_id TEXT,
      query TEXT,
      created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # Default Settings
    default_settings_json = json.dumps({"wv": 0.6, "wg": 0.4, "synergy": 1.4, "depth": 1.3})

    # Add Liam
    cursor.execute("SELECT id FROM users WHERE id = 'liam'")
    if not cursor.fetchone():
        logger.info("Inserting user: liam (Admin)")
        cursor.execute("""
        INSERT INTO users (id, name, role, password_hash, is_admin, settings_json)
        VALUES (?, ?, ?, ?, ?, ?)
        """, ('liam', 'Liam (Admin)', 'System Administrator', get_password_hash('qorwnsdn87'), 1, default_settings_json))

    # Add User B
    cursor.execute("SELECT id FROM users WHERE id = 'userB'")
    if not cursor.fetchone():
        logger.info("Inserting user: userB (Recruiter)")
        cursor.execute("""
        INSERT INTO users (id, name, role, password_hash, is_admin, settings_json)
        VALUES (?, ?, ?, ?, ?, ?)
        """, ('userB', 'Recruiter B', 'Tech Recruiter', get_password_hash('user1234'), 0, default_settings_json))

    conn.commit()
    conn.close()
    logger.info("DB Initialization complete!")

if __name__ == "__main__":
    init_db()
