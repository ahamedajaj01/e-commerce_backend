import os
import sys
import subprocess

def reset():
    print("====================================")
    print("    DATABASE WIPE & RESET UTILITY   ")
    print("====================================\n")
    
    db_file = "db_v2.sqlite3"
    
    # 1. Delete SQLite file
    if os.path.exists(db_file):
        print(f"🗑️  Deleting {db_file}...")
        try:
            os.remove(db_file)
            print("✅ Successfully deleted old database.\n")
        except Exception as e:
            print(f"❌ Error deleting database: {e}")
            print("Make sure you stop the server first (Ctrl+C) before wiping the database.")
            sys.exit(1)
    else:
        print("⚠️ No existing database found, proceeding to creation.\n")

    # 2. Run Migrations
    print("🏗️  Rebuilding database schema...")
    result = subprocess.run([sys.executable, "manage.py", "migrate"])
    
    if result.returncode == 0:
        print("\n✅ Success! Database is now completely clean and empty.")
        print("You may now create a new superuser via: python manage.py createsuperuser")
    else:
        print("\n❌ An error occurred while migrating the database.")

if __name__ == "__main__":
    confirm = input("⚠️  WARNING: This will permanently delete all data (users, products, orders). Type 'yes' to proceed: ")
    if confirm.lower() == 'yes':
        reset()
    else:
        print("Operation cancelled.")
