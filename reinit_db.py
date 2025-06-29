#!/usr/bin/env python3
"""
Database Reinitialization Script

This script removes the existing database and creates a fresh one with no entries.
Useful for starting with a clean setup for testing and validation.

Usage:
    python reinit_db.py [--force] [--non-interactive]
"""

import os
import sys
import argparse
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

print(f"[INFO] Python executable: {sys.executable}")
print(f"[INFO] sys.prefix: {sys.prefix}")
print(f"[INFO] VIRTUAL_ENV: {os.environ.get('VIRTUAL_ENV', 'not set')}")

def reinit_database(force=False, non_interactive=False):
    """Remove and reinitialize the database."""
    db_path = Path("./data/tasks.db")
    
    print("🗄️ Database Reinitialization")
    print("=" * 40)
    
    # Check if database exists
    if db_path.exists():
        # Get current task count before deletion
        try:
            from data_store.task_store import TaskStore
            store = TaskStore()
            current_count = store.get_task_count()
            print(f"📊 Current database contains {current_count} tasks")
        except Exception as e:
            print(f"⚠️ Could not read current task count: {e}")
        
        # Confirm deletion (unless forced or non-interactive)
        print(f"\n🗑️ Removing existing database: {db_path}")
        
        if force or non_interactive:
            print("✅ Proceeding with deletion (forced/non-interactive mode)")
        else:
            response = input("Are you sure you want to delete all tasks? (yes/no): ").lower().strip()
            
            if response not in ['yes', 'y']:
                print("❌ Database reinitialization cancelled")
                return False
        
        try:
            db_path.unlink()
            print("✅ Database file removed successfully")
        except Exception as e:
            print(f"❌ Error removing database: {e}")
            return False
    else:
        print("ℹ️ No existing database found")
    
    # Reinitialize the database
    print("\n🔄 Reinitializing database...")
    try:
        from data_store.task_store import TaskStore
        store = TaskStore()
        store.init_db()
        print("✅ Database reinitialized successfully!")
        print(f"📁 Database location: {db_path.absolute()}")
        
        # Verify the new database
        new_count = store.get_task_count()
        print(f"📊 New database contains {new_count} tasks")
        
        return True
    except Exception as e:
        print(f"❌ Error reinitializing database: {e}")
        return False

def main():
    """Main function."""
    parser = argparse.ArgumentParser(description='Reinitialize the database')
    parser.add_argument('--force', action='store_true', help='Force reinitialization without confirmation')
    parser.add_argument('--non-interactive', action='store_true', help='Non-interactive mode (no user prompts)')
    
    args = parser.parse_args()
    
    try:
        success = reinit_database(force=args.force, non_interactive=args.non_interactive)
        
        if success:
            print("\n" + "=" * 40)
            print("🎉 Database reinitialization completed!")
            print("=" * 40)
            print("\n💡 Next steps:")
            print("   1. Start services: python scripts/start_all.py")
            print("   2. Test functionality: python test_tool_calling.py")
            print("   3. Run demo: python scripts/run_demo.py")
            print("   4. Use CLI: python cli/task_manager_cli.py")
            return 0
        else:
            print("\n❌ Database reinitialization failed")
            return 1
            
    except KeyboardInterrupt:
        print("\n\n❌ Database reinitialization interrupted by user")
        return 1
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 