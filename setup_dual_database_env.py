#!/usr/bin/env python3
"""
Setup environment variables for dual database system (KG and US)
"""

def main():
    print("🌍 Dual Database Environment Setup")
    print("=" * 50)
    
    print("You have two separate Railway databases:")
    print("🇰🇬 marque_db_kg - For Kyrgyzstan market")
    print("🇺🇸 marque_db_us - For United States market")
    print()
    
    print("To set up both databases, you need to:")
    print()
    print("1. 🌐 Go to your Railway dashboard")
    print("2. 📁 Click on 'marque_db_kg' project")
    print("3. 🐘 Click on the PostgreSQL service")
    print("4. ⚙️  Go to 'Variables' tab")
    print("5. 📋 Copy the DATABASE_URL (external one, not .internal)")
    print()
    print("6. 🔄 Repeat for 'marque_db_us' project")
    print()
    print("7. 📝 Add both URLs to your .env file:")
    print()
    print("DATABASE_URL_MARQUE_KG=postgresql://user:password@host:port/database")
    print("DATABASE_URL_MARQUE_US=postgresql://user:password@host:port/database")
    print()
    print("🔗 Example format:")
    print("DATABASE_URL_MARQUE_KG=postgresql://postgres:abc123@containers-us-west-123.railway.app:5432/railway")
    print("DATABASE_URL_MARQUE_US=postgresql://postgres:xyz789@containers-us-west-456.railway.app:5432/railway")
    print()
    print("⚠️  Important:")
    print("- Make sure URLs don't contain 'railway.internal'")
    print("- Each database should have its own unique URL")
    print("- URLs should end with .railway.app or .rlwy.net")
    print()
    print("🚀 After updating .env file, run:")
    print("python3 setup_kg_database.py")
    print("python3 setup_us_database.py")

if __name__ == "__main__":
    main()
