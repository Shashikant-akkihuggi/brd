"""
Migration script to add role column to users table.
Run this once to upgrade the database schema for RBAC.
"""
import sqlite3
import os

def migrate():
    # Get the correct database path
    db_path = os.path.join(os.path.dirname(__file__), 'brd_platform.db')
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Check if role column already exists
    cursor.execute("PRAGMA table_info(users)")
    columns = [column[1] for column in cursor.fetchall()]
    
    if 'role' in columns:
        print("✅ role column already exists in users table")
        conn.close()
        return
    
    # Add role column with default value 'viewer'
    cursor.execute("""
        ALTER TABLE users 
        ADD COLUMN role VARCHAR DEFAULT 'viewer' NOT NULL
    """)
    
    # Update existing users to have viewer role
    cursor.execute("""
        UPDATE users 
        SET role = 'viewer' 
        WHERE role IS NULL OR role = ''
    """)
    
    conn.commit()
    conn.close()
    
    print("✅ Successfully added role column to users table")
    print("✅ All existing users set to 'viewer' role")
    print("✅ Migration complete!")
    print("\n📝 To create an admin user, use the /api/auth/update-role endpoint")
    print("   or manually update the database:")
    print("   UPDATE users SET role = 'admin' WHERE email = 'your-email@example.com';")

if __name__ == "__main__":
    print("🔄 Running migration: Add role column to users table")
    migrate()
