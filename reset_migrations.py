#!/usr/bin/env python3
"""
Migration Reset Script
======================
This script will:
1. Backup current databases (just in case)
2. Delete all migration files
3. Delete the databases
4. Create fresh initial migration
5. Apply migration to both KG and US databases

⚠️ WARNING: This will delete all your data! Make sure you have backups if needed.
"""

import os
import sys
import shutil
from datetime import datetime
from pathlib import Path

# Colors for terminal output
class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    END = '\033[0m'

def print_step(message):
    """Print a step message"""
    print(f"\n{Colors.BLUE}{Colors.BOLD}➜ {message}{Colors.END}")

def print_success(message):
    """Print a success message"""
    print(f"{Colors.GREEN}✓ {message}{Colors.END}")

def print_warning(message):
    """Print a warning message"""
    print(f"{Colors.YELLOW}⚠ {message}{Colors.END}")

def print_error(message):
    """Print an error message"""
    print(f"{Colors.RED}✗ {message}{Colors.END}")

def confirm_action():
    """Ask for user confirmation"""
    print(f"\n{Colors.YELLOW}{Colors.BOLD}⚠️  WARNING ⚠️{Colors.END}")
    print(f"{Colors.RED}This will DELETE all migrations and databases!{Colors.END}")
    print(f"{Colors.YELLOW}All your data will be lost unless you have backups.{Colors.END}\n")
    
    response = input("Are you sure you want to continue? Type 'yes' to proceed: ")
    return response.lower() == 'yes'

def backup_databases():
    """Backup existing databases"""
    print_step("Step 1: Backing up existing databases")
    
    backup_dir = Path("databases/backups")
    backup_dir.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    databases = [
        "databases/marque_kg.db",
        "databases/marque_us.db",
        "databases/kg_market.db"
    ]
    
    backed_up = []
    for db_path in databases:
        if os.path.exists(db_path):
            db_name = os.path.basename(db_path)
            backup_path = backup_dir / f"{db_name}.backup_{timestamp}"
            shutil.copy2(db_path, backup_path)
            backed_up.append(backup_path)
            print_success(f"Backed up {db_path} → {backup_path}")
    
    if backed_up:
        print_success(f"Backed up {len(backed_up)} database(s)")
    else:
        print_warning("No databases found to backup")

def delete_migration_files():
    """Delete all migration files except __init__.py"""
    print_step("Step 2: Deleting all migration files")
    
    versions_dir = Path("alembic/versions")
    if not versions_dir.exists():
        print_warning("No versions directory found")
        return
    
    deleted_count = 0
    for file in versions_dir.glob("*.py"):
        if file.name != "__init__.py":
            file.unlink()
            deleted_count += 1
            print_success(f"Deleted {file.name}")
    
    # Also delete .pyc files
    for file in versions_dir.glob("*.pyc"):
        file.unlink()
    
    print_success(f"Deleted {deleted_count} migration file(s)")

def delete_databases():
    """Delete all database files"""
    print_step("Step 3: Deleting database files")
    
    databases = [
        "databases/marque_kg.db",
        "databases/marque_us.db",
        "databases/kg_market.db",
        "test.db",
        "test_product_assets.db",
        "test_product_catalog.db",
        "test_product_search.db"
    ]
    
    deleted_count = 0
    for db_path in databases:
        if os.path.exists(db_path):
            os.remove(db_path)
            deleted_count += 1
            print_success(f"Deleted {db_path}")
    
    # Also delete any -wal and -shm files (SQLite WAL mode)
    for ext in ["-wal", "-shm"]:
        for db_path in databases:
            wal_file = db_path + ext
            if os.path.exists(wal_file):
                os.remove(wal_file)
                print_success(f"Deleted {wal_file}")
    
    print_success(f"Deleted {deleted_count} database file(s)")

def create_initial_migration():
    """Create a fresh initial migration"""
    print_step("Step 4: Creating fresh initial migration")
    
    print("Running: alembic revision --autogenerate -m 'initial_migration'")
    exit_code = os.system("alembic revision --autogenerate -m 'initial_migration'")
    
    if exit_code == 0:
        print_success("Created initial migration")
    else:
        print_error("Failed to create migration")
        sys.exit(1)

def apply_migration_kg():
    """Apply migration to KG database"""
    print_step("Step 5: Applying migration to KG database")
    
    # Make sure the databases directory exists
    os.makedirs("databases", exist_ok=True)
    
    print("Running: alembic upgrade head (KG)")
    exit_code = os.system("alembic upgrade head")
    
    if exit_code == 0:
        print_success("Applied migration to KG database")
    else:
        print_error("Failed to apply migration to KG database")
        sys.exit(1)

def apply_migration_us():
    """Apply migration to US database"""
    print_step("Step 6: Applying migration to US database")
    
    print("Running: ALEMBIC_TARGET_DB=US alembic upgrade head")
    exit_code = os.system("ALEMBIC_TARGET_DB=US alembic upgrade head")
    
    if exit_code == 0:
        print_success("Applied migration to US database")
    else:
        print_error("Failed to apply migration to US database")
        sys.exit(1)

def verify_databases():
    """Verify that databases were created"""
    print_step("Step 7: Verifying databases")
    
    databases = [
        "databases/marque_kg.db",
        "databases/marque_us.db"
    ]
    
    all_good = True
    for db_path in databases:
        if os.path.exists(db_path):
            size = os.path.getsize(db_path)
            print_success(f"✓ {db_path} exists (size: {size} bytes)")
        else:
            print_error(f"✗ {db_path} does NOT exist!")
            all_good = False
    
    return all_good

def main():
    """Main execution function"""
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*70}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'Migration Reset Script':^70}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*70}{Colors.END}\n")
    
    # Check if we're in the right directory
    if not os.path.exists("alembic"):
        print_error("Error: alembic directory not found!")
        print_error("Make sure you're running this script from the project root directory.")
        sys.exit(1)
    
    # Ask for confirmation
    if not confirm_action():
        print_warning("\nOperation cancelled by user.")
        sys.exit(0)
    
    try:
        # Execute all steps
        backup_databases()
        delete_migration_files()
        delete_databases()
        create_initial_migration()
        apply_migration_kg()
        apply_migration_us()
        
        # Verify
        if verify_databases():
            print(f"\n{Colors.GREEN}{Colors.BOLD}{'='*70}{Colors.END}")
            print(f"{Colors.GREEN}{Colors.BOLD}{'🎉 SUCCESS! Migration reset complete! 🎉':^70}{Colors.END}")
            print(f"{Colors.GREEN}{Colors.BOLD}{'='*70}{Colors.END}\n")
            
            print(f"{Colors.BOLD}Next steps:{Colors.END}")
            print("1. Start your FastAPI server")
            print("2. Test your API endpoints to ensure data saves correctly")
            print("3. If you need sample data, run your data population scripts")
            print(f"\n{Colors.YELLOW}Note: Your backup databases are in 'databases/backups/'{Colors.END}\n")
        else:
            print_error("\n⚠️  Some databases were not created successfully!")
            print_error("Please check the error messages above.")
            sys.exit(1)
    
    except KeyboardInterrupt:
        print_warning("\n\nOperation interrupted by user.")
        sys.exit(1)
    except Exception as e:
        print_error(f"\n\nAn error occurred: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()

