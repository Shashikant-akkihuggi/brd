"""
Migration script to add refresh_tokens table to existing database.
Run this once to upgrade the database schema.
"""
import sqlite3
from datetime import datetime

def migrate():
    conn = sqlite3.connect('brd_platform.db')
    cursor = conn.cursor()
    
    # Check if table already exists
    cursor.execute("""
        SELECT name FROM sqlite_master 
        WHERE type='table' AND name='refresh_tokens'
    """)
    
    if cursor.fetchone():
        print("✅ refresh_tokens table already exists")
        conn.close()
        return
    
    # Create refresh_tokens table
    cursor.execute("""
        CREATE TABLE refresh_tokens (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            token VARCHAR NOT NULL UNIQUE,
            expires_at DATETIME NOT NULL,
            is_revoked BOOLEAN DEFAULT 0,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    """)
    
    # Create index on token for faster lookups
    cursor.execute("""
        CREATE INDEX ix_refresh_tokens_token ON refresh_tokens (token)
    """)
    
    # Create index on user_id
    cursor.execute("""
        CREATE INDEX ix_refresh_tokens_user_id ON refresh_tokens (user_id)
    """)
    
    conn.commit()
    conn.close()
    
    print("✅ Successfully created refresh_tokens table")
    print("✅ Migration complete!")

if __name__ == "__main__":
    print("🔄 Running migration: Add refresh_tokens table")
    migrate()
