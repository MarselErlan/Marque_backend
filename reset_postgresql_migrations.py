#!/usr/bin/env python3
"""
PostgreSQL Migration Reset Script
==================================
This script will:
1. Connect to both KG and US PostgreSQL databases
2. Drop ALL tables (including alembic_version)
3. Delete all migration files
4. Create fresh initial migration
5. Apply migration to both databases

⚠️ WARNING: This will delete ALL data in your databases!
"""

import os
import sys
from pathlib import Path
from datetime import datetime

# Add src to path
sys.path.insert(0, os.path.realpath('.'))

from sqlalchemy import create_engine, text, inspect
from dotenv import load_dotenv

load_dotenv()

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
    print(f"{Colors.RED}This will DELETE ALL TABLES from your PostgreSQL databases!{Colors.END}")
    print(f"{Colors.YELLOW}ALL DATA will be lost from both KG and US databases on Railway!{Colors.END}\n")
    
    print(f"{Colors.BOLD}This affects:{Colors.END}")
    print("  • All users")
    print("  • All products") 
    print("  • All orders")
    print("  • All carts and wishlists")
    print("  • Everything!\n")
    
    response = input("Are you ABSOLUTELY sure? Type 'DELETE ALL DATA' to proceed: ")
    return response == 'DELETE ALL DATA'

def drop_all_tables(database_url, market_name):
    """Drop all tables from database"""
    print_step(f"Dropping all tables from {market_name} database")
    
    try:
        engine = create_engine(database_url)
        
        with engine.connect() as conn:
            # Get list of all tables
            inspector = inspect(engine)
            tables = inspector.get_table_names()
            
            if not tables:
                print_warning(f"No tables found in {market_name} database")
                return
            
            print(f"Found {len(tables)} tables in {market_name} database")
            
            # Drop all tables (including alembic_version)
            conn.execute(text("DROP SCHEMA public CASCADE;"))
            conn.execute(text("CREATE SCHEMA public;"))
            conn.execute(text("GRANT ALL ON SCHEMA public TO postgres;"))
            conn.execute(text("GRANT ALL ON SCHEMA public TO public;"))
            conn.commit()
            
            print_success(f"Dropped all tables from {market_name} database")
    
    except Exception as e:
        print_error(f"Error dropping tables from {market_name}: {e}")
        raise

def delete_migration_files():
    """Delete all migration files except __init__.py"""
    print_step("Deleting all migration files")
    
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
    
    # Delete __pycache__
    pycache = versions_dir / "__pycache__"
    if pycache.exists():
        for file in pycache.glob("*"):
            file.unlink()
        pycache.rmdir()
    
    print_success(f"Deleted {deleted_count} migration file(s)")

def create_initial_migration():
    """Create a fresh initial migration"""
    print_step("Creating fresh initial migration")
    
    print("Running: alembic revision --autogenerate -m 'initial_migration'")
    exit_code = os.system("alembic revision --autogenerate -m 'initial_migration'")
    
    if exit_code == 0:
        print_success("Created initial migration")
    else:
        print_error("Failed to create migration")
        sys.exit(1)

def apply_migration_kg():
    """Apply migration to KG database"""
    print_step("Applying migration to KG database")
    
    print("Running: alembic upgrade head (KG)")
    exit_code = os.system("alembic upgrade head")
    
    if exit_code == 0:
        print_success("Applied migration to KG database")
    else:
        print_error("Failed to apply migration to KG database")
        sys.exit(1)

def apply_migration_us():
    """Apply migration to US database"""
    print_step("Applying migration to US database")
    
    print("Running: ALEMBIC_TARGET_DB=US alembic upgrade head")
    exit_code = os.system("ALEMBIC_TARGET_DB=US alembic upgrade head")
    
    if exit_code == 0:
        print_success("Applied migration to US database")
    else:
        print_error("Failed to apply migration to US database")
        sys.exit(1)

def verify_databases(kg_url, us_url):
    """Verify that tables were created"""
    print_step("Verifying databases")
    
    try:
        # Check KG database
        kg_engine = create_engine(kg_url)
        inspector = inspect(kg_engine)
        kg_tables = inspector.get_table_names()
        
        print_success(f"✓ KG database has {len(kg_tables)} tables")
        
        # Check US database
        us_engine = create_engine(us_url)
        inspector = inspect(us_engine)
        us_tables = inspector.get_table_names()
        
        print_success(f"✓ US database has {len(us_tables)} tables")
        
        return len(kg_tables) > 0 and len(us_tables) > 0
    
    except Exception as e:
        print_error(f"Error verifying databases: {e}")
        return False

def main():
    """Main execution function"""
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*70}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'PostgreSQL Migration Reset Script':^70}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*70}{Colors.END}\n")
    
    # Get database URLs
    from src.app_01.core.config import settings
    kg_url = settings.database.url_kg
    us_url = settings.database.url_us
    
    print(f"KG Database: {kg_url.split('@')[1] if '@' in kg_url else kg_url}")
    print(f"US Database: {us_url.split('@')[1] if '@' in us_url else us_url}")
    
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
        drop_all_tables(kg_url, "KG")
        drop_all_tables(us_url, "US")
        delete_migration_files()
        create_initial_migration()
        apply_migration_kg()
        apply_migration_us()
        
        # Verify
        if verify_databases(kg_url, us_url):
            print(f"\n{Colors.GREEN}{Colors.BOLD}{'='*70}{Colors.END}")
            print(f"{Colors.GREEN}{Colors.BOLD}{'🎉 SUCCESS! Migration reset complete! 🎉':^70}{Colors.END}")
            print(f"{Colors.GREEN}{Colors.BOLD}{'='*70}{Colors.END}\n")
            
            print(f"{Colors.BOLD}Next steps:{Colors.END}")
            print("1. Your databases are now clean with fresh schema")
            print("2. Populate sample data: python populate_databases.py")
            print("3. Start your server: uvicorn src.app_01.main:app --reload")
            print("4. Test your API endpoints")
        else:
            print_error("\n⚠️  Some tables were not created successfully!")
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

