"""
Check US Railway Database for users
"""
import psycopg2
from psycopg2.extras import RealDictCursor

US_DB = "postgresql://postgres:HnxnpmuFbMiTFmOFJQkfhTDjaublaith@interchange.proxy.rlwy.net:54878/railway"

def check_us_database():
    """Check US Railway database for users"""
    print("🔍 Checking US Railway Database")
    print("=" * 80)
    print(f"Database: {US_DB.split('@')[1][:30]}...")
    print()
    
    try:
        conn = psycopg2.connect(US_DB)
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # Get all users
        cursor.execute("SELECT * FROM users ORDER BY id DESC LIMIT 20")
        users = cursor.fetchall()
        
        print(f"📊 Total users (showing last 20): {len(users)}")
        print()
        
        if not users:
            print("❌ No users found in US database yet")
            print()
            print("💡 TIP: Run test_auth_flow_complete.py with a US phone number (+1...)")
            print("   After adding DATABASE_URL_MARQUE_US to Railway, new users will appear here!")
        else:
            for user in users:
                print(f"User ID {user['id']}: {user['phone_number']}")
                if user.get('full_name'):
                    print(f"  Name: {user['full_name']}")
                print(f"  Active: {user['is_active']}, Verified: {user['is_verified']}")
                if user.get('last_login'):
                    print(f"  Last Login: {user['last_login']}")
                print()
        
        # Statistics
        cursor.execute("""
            SELECT 
                COUNT(*) as total,
                COUNT(*) FILTER (WHERE phone_number LIKE '+1%') as us_users,
                COUNT(*) FILTER (WHERE is_active = true) as active,
                COUNT(*) FILTER (WHERE is_verified = true) as verified
            FROM users
        """)
        stats = cursor.fetchone()
        
        print("📈 Database statistics:")
        print("-" * 80)
        print(f"  Total users: {stats['total']}")
        print(f"  US users (+1): {stats['us_users']}")
        print(f"  Active: {stats['active']}")
        print(f"  Verified: {stats['verified']}")
        print()
        
        conn.close()
        
        print("=" * 80)
        print("✅ US database check complete!")
        
    except Exception as e:
        print(f"❌ Error connecting to US database: {e}")
        print()
        print("💡 Make sure:")
        print("  1. The US Railway PostgreSQL service is running")
        print("  2. The connection URL is correct")
        print("  3. The 'users' table exists")

if __name__ == "__main__":
    check_us_database()

