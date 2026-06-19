"""
Database Manager Module — MahesaVault
Handles local SQLite database for the Secure Vault feature.
Allows users to create accounts and save their encrypted files/messages.
"""

import sqlite3
import hashlib
import os
from datetime import datetime

# Database path in the root folder
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'mahesavault.db')

def init_db():
    """Initialize the database tables if they don't exist."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Users table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        created_at TEXT NOT NULL
    )
    ''')
    
    # Vault items table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS vault_items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        title TEXT NOT NULL,
        content TEXT NOT NULL,
        item_type TEXT NOT NULL, -- 'TEXT', 'FILE_B64', 'IMAGE_B64'
        encryption_algo TEXT,
        created_at TEXT NOT NULL,
        FOREIGN KEY (user_id) REFERENCES users (id)
    )
    ''')
    
    conn.commit()
    conn.close()

def _hash_password(password: str) -> str:
    """Hash password using SHA-256 for basic security."""
    return hashlib.sha256(password.encode()).hexdigest()

def create_user(username: str, password: str) -> bool:
    """Create a new user. Returns True if successful, False if exists."""
    init_db()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        cursor.execute(
            "INSERT INTO users (username, password_hash, created_at) VALUES (?, ?, ?)",
            (username, _hash_password(password), datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        )
        conn.commit()
        success = True
    except sqlite3.IntegrityError:
        success = False
    finally:
        conn.close()
        
    return success

def authenticate_user(username: str, password: str) -> int:
    """Authenticate a user. Returns user_id if successful, None otherwise."""
    init_db()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute(
        "SELECT id FROM users WHERE username = ? AND password_hash = ?",
        (username, _hash_password(password))
    )
    result = cursor.fetchone()
    conn.close()
    
    return result[0] if result else None

def save_vault_item(user_id: int, title: str, content: str, item_type: str, encryption_algo: str = "None") -> bool:
    """Save an item to the user's vault."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        cursor.execute(
            '''INSERT INTO vault_items 
               (user_id, title, content, item_type, encryption_algo, created_at) 
               VALUES (?, ?, ?, ?, ?, ?)''',
            (user_id, title, content, item_type, encryption_algo, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        )
        conn.commit()
        success = True
    except Exception as e:
        print(f"DB Error: {e}")
        success = False
    finally:
        conn.close()
        
    return success

def get_vault_items(user_id: int) -> list:
    """Retrieve all vault items for a user."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # Return dict-like objects
    cursor = conn.cursor()
    
    cursor.execute(
        "SELECT id, title, content, item_type, encryption_algo, created_at FROM vault_items WHERE user_id = ? ORDER BY created_at DESC",
        (user_id,)
    )
    items = [dict(row) for row in cursor.fetchall()]
    conn.close()
    
    return items

def delete_vault_item(item_id: int, user_id: int) -> bool:
    """Delete a vault item, ensuring it belongs to the user."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("DELETE FROM vault_items WHERE id = ? AND user_id = ?", (item_id, user_id))
    rows_affected = cursor.rowcount
    conn.commit()
    conn.close()
    
    return rows_affected > 0
