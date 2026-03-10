"""
Migration script to rename user_id to owner_id in projects table.
Run this once to upgrade the database schema for project ownership.
"""
import sqlite3
import os

def migrate():
    # Get the correct database path
    db_path = os.path.join(os.path.dirname(__file__), 'brd_platform.db')
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Check if owner_id column already exists
    cursor.execute("PRAGMA table_info(projects)")
    columns = [column[1] for column in cursor.fetchall()]
    
    if 'owner_id' in columns:
        print("✅ owner_id column already exists in projects table")
        conn.close()
        return
    
    if 'user_id' not in columns:
        print("❌ user_id column not found in projects table")
        print("   The table might already be migrated or doesn't exist yet")
        conn.close()
        return
    
    print("🔄 Renaming user_id to owner_id in projects table...")
    
    # SQLite doesn't support ALTER COLUMN RENAME directly
    # We need to create a new table and copy data
    
    # 1. Create new table with owner_id
    cursor.execute("""
        CREATE TABLE projects_new (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            owner_id INTEGER NOT NULL,
            name VARCHAR NOT NULL,
            description TEXT,
            keywords JSON,
            start_date DATETIME,
            end_date DATETIME,
            created_at DATETIME,
            updated_at DATETIME,
            FOREIGN KEY (owner_id) REFERENCES users (id)
        )
    """)
    
    # 2. Copy data from old table to new table
    cursor.execute("""
        INSERT INTO projects_new (id, owner_id, name, description, keywords, start_date, end_date, created_at, updated_at)
        SELECT id, user_id, name, description, keywords, start_date, end_date, created_at, updated_at
        FROM projects
    """)
    
    # 3. Drop old table
    cursor.execute("DROP TABLE projects")
    
    # 4. Rename new table to projects
    cursor.execute("ALTER TABLE projects_new RENAME TO projects")
    
    # 5. Create index on owner_id
    cursor.execute("CREATE INDEX ix_projects_owner_id ON projects (owner_id)")
    
    conn.commit()
    conn.close()
    
    print("✅ Successfully renamed user_id to owner_id in projects table")
    print("✅ Created index on owner_id for better query performance")
    print("✅ Migration complete!")

if __name__ == "__main__":
    print("🔄 Running migration: Rename user_id to owner_id in projects table")
    migrate()
