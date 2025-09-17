#!/usr/bin/env python3
"""
Help identify the correct Railway database URLs
"""

def main():
    print("🔍 Railway Database URL Identification")
    print("=" * 50)
    
    print("From your Railway Variables tab, you have these database-related variables:")
    print()
    print("📋 Available Variables:")
    print("   🔗 DATABASE_URL - Main database connection string")
    print("   🌐 DATABASE_PUBLIC_URL - Public database connection string")
    print("   🏠 PGHOST - Database hostname")
    print("   🔌 PGPORT - Database port")
    print("   📁 PGDATABASE - Database name")
    print("   👤 PGUSER - Database username")
    print("   🔐 PGPASSWORD - Database password")
    print()
    print("✅ RECOMMENDED: Use DATABASE_URL")
    print("   - This is the complete connection string")
    print("   - Contains all connection details")
    print("   - Ready to use with SQLAlchemy")
    print()
    print("🔍 How to get the correct DATABASE_URL:")
    print("1. Click on the eye icon (◒) next to DATABASE_URL")
    print("2. Copy the revealed URL")
    print("3. Make sure it doesn't contain 'railway.internal'")
    print("4. Should look like: postgresql://user:password@host:port/database")
    print()
    print("⚠️  Alternative: Use individual components")
    print("If DATABASE_URL doesn't work, you can construct it from:")
    print("   postgresql://PGUSER:PGPASSWORD@PGHOST:PGPORT/PGDATABASE")
    print()
    print("🚀 Next steps:")
    print("1. Click the eye icon next to DATABASE_URL")
    print("2. Copy the revealed URL")
    print("3. Add it to your .env file as:")
    print("   DATABASE_URL_MARQUE_KG=your_copied_url")
    print("4. Repeat for marque_db_us project")
    print("5. Run: python3 setup_kg_database.py")

if __name__ == "__main__":
    main()
