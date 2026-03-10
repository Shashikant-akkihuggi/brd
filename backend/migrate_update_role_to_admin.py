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
        print("❌ Users table not found")
        conn.close()
        return
    
    # Check if role column exists
    cursor.execute("PRAGMA table_info(users)")
    columns = [column[1] for column in cursor.fetchall()]
    
    if 'role' not in columns:
        print("❌ Role column not found in users table")
        conn.close()
        return
    
    # Count users with viewer role
    cursor.execute("SELECT COUNT(*) FROM users WHERE role = 'viewer'")
    viewer_count = cursor.fetchone()[0]
    
    print(f"🔄 Found {viewer_count} user(s) with 'viewer' role")
    
    if viewer_count == 0:
        print("✅ No users need to be updated")
        conn.close()
        return
    
    # Update all viewer users to admin
    cursor.execute("UPDATE users SET role = 'admin' WHERE role = 'viewer'")
    
    conn.commit()
    
    # Verify update
    cursor.execute("SELECT COUNT(*) FROM users WHERE role = 'admin'")
    admin_count = cursor.fetchone()[0]
    
    conn.close()
    
    print(f"✅ Successfully updated {viewer_count} user(s) to 'admin' role")
    print(f"✅ Total admin users: {admin_count}")
    print("✅ Migration complete!")
    print("\n📝 Note: New users will now be created with 'admin' role by default")

if __name__ == "__main__":
    print("🔄 Running migration: Update default role to admin")
    print("="*70)
    migrate()
