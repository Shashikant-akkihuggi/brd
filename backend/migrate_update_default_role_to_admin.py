"""
Migration script to update default role from viewer to admin.
Updates all existing users with viewer role to admin role.
"""
import sqlite3
import os

def migrate():
    # Get the correct database path
    db_path = os.path.join(os.path.dirname(__file__), 'brd_platform.db')
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Check if users table exists
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
    if not cursor.fetchone():
        print("❌ Users ta