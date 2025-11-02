"""Utility script to fix admin user in existing database."""
import sys
import io
from config.settings import DatabaseConfig
from data.database import DatabaseManager, User
from sqlalchemy import text

# Fix Unicode encoding for Windows console
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

def add_is_admin_column(db_manager):
    """Add is_admin column to users table if it doesn't exist."""
    try:
        session = db_manager.get_session()
        try:
            # Check if column exists
            result = session.execute(text("PRAGMA table_info(users)"))
            columns = [row[1] for row in result.fetchall()]
            
            if 'is_admin' not in columns:
                print("Adding is_admin column to users table...")
                session.execute(text("ALTER TABLE users ADD COLUMN is_admin BOOLEAN DEFAULT 0"))
                session.commit()
                print("✓ Column added successfully")
                return True
            else:
                print("✓ is_admin column already exists")
                return True
        finally:
            session.close()
    except Exception as e:
        print(f"Error adding column: {str(e)}")
        return False

def fix_admin_user(database_path: str = "metrics.db"):
    """Fix or create admin user with correct privileges."""
    print("Fixing admin user...")
    
    config = DatabaseConfig(db_type="sqlite", database=database_path)
    
    try:
        db_manager = DatabaseManager(config)
        
        # First, ensure is_admin column exists
        if not add_is_admin_column(db_manager):
            print("Failed to add is_admin column")
            return False
        
        session = db_manager.get_session()
        
        try:
            admin_user = session.query(User).filter(User.username == "admin").first()
            
            if admin_user:
                print(f"✓ Admin user found")
                
                # Verify password
                if db_manager.verify_password("admin123", admin_user.password_hash):
                    print("✓ Password verified")
                    
                    # Update is_admin flag
                    if not admin_user.is_admin:
                        admin_user.is_admin = True
                        session.commit()
                        print("✅ Updated admin user privileges (is_admin = True)")
                    else:
                        print("✓ Admin user already has admin privileges")
                else:
                    # Reset password to admin123
                    print("⚠️  Password doesn't match. Resetting password...")
                    admin_user.password_hash = db_manager.hash_password("admin123")
                    admin_user.is_admin = True
                    session.commit()
                    print("✅ Reset admin password and privileges")
                    print("   Username: admin")
                    print("   Password: admin123")
            else:
                # Create admin user
                print("⚠️  Admin user not found. Creating...")
                if db_manager.create_user("admin", "admin123", None, is_admin=True):
                    print("✅ Admin user created successfully!")
                    print("   Username: admin")
                    print("   Password: admin123")
                    print("   ⚠️  Please change the default password after first login!")
                else:
                    print("❌ Failed to create admin user")
                    
        finally:
            session.close()
            
        print("\n✓ Admin user fix complete!")
        return True
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    db_path = sys.argv[1] if len(sys.argv) > 1 else "metrics.db"
    success = fix_admin_user(db_path)
    sys.exit(0 if success else 1)

