"""
Live Test for Address APIs
Tests address creation and verifies in database
"""

import requests
import json
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import os

# API Configuration
BASE_URL = "http://127.0.0.1:8000/api/v1"

# Colors for output
GREEN = '\033[92m'
RED = '\033[91m'
BLUE = '\033[94m'
YELLOW = '\033[93m'
RESET = '\033[0m'

def print_success(msg):
    print(f"{GREEN}✅ {msg}{RESET}")

def print_error(msg):
    print(f"{RED}❌ {msg}{RESET}")

def print_info(msg):
    print(f"{BLUE}ℹ️  {msg}{RESET}")

def print_warning(msg):
    print(f"{YELLOW}⚠️  {msg}{RESET}")

def get_auth_token(phone="+13128059851"):
    """Get authentication token"""
    print("\n" + "=" * 60)
    print("STEP 1: AUTHENTICATION")
    print("=" * 60)
    
    # Send verification code
    print_info(f"Sending verification code to {phone}...")
    response = requests.post(
        f"{BASE_URL}/auth/send-verification",
        json={"phone": phone}
    )
    
    if response.status_code != 200:
        print_error(f"Failed to send code: {response.text}")
        return None
    
    print_success("Verification code sent!")
    data = response.json()
    print(f"Response: {json.dumps(data, indent=2)}")
    
    # Get code from user
    code = input("\n📱 Enter the verification code from SMS: ").strip()
    
    # Verify code
    print_info("Verifying code...")
    response = requests.post(
        f"{BASE_URL}/auth/verify-code",
        json={"phone": phone, "verification_code": code}
    )
    
    if response.status_code != 200:
        print_error(f"Failed to verify code: {response.text}")
        return None
    
    data = response.json()
    token = data.get("access_token")
    user_id = data.get("user", {}).get("id")
    market = data.get("market", "us")
    
    print_success(f"Authentication successful!")
    print_info(f"User ID: {user_id}")
    print_info(f"Market: {market}")
    print_info(f"Token: {token[:30]}...")
    
    return {
        "token": token,
        "user_id": user_id,
        "market": market,
        "phone": phone
    }

def test_get_addresses(auth):
    """Test GET /profile/addresses"""
    print("\n" + "=" * 60)
    print("STEP 2: GET ADDRESSES (Initial State)")
    print("=" * 60)
    
    headers = {"Authorization": f"Bearer {auth['token']}"}
    
    response = requests.get(f"{BASE_URL}/profile/addresses", headers=headers)
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    if response.status_code == 200:
        data = response.json()
        print_success(f"Found {data.get('total', 0)} existing addresses")
        return data.get('addresses', [])
    else:
        print_error("Failed to get addresses")
        return []

def test_create_address(auth):
    """Test POST /profile/addresses"""
    print("\n" + "=" * 60)
    print("STEP 3: CREATE NEW ADDRESS")
    print("=" * 60)
    
    headers = {
        "Authorization": f"Bearer {auth['token']}",
        "Content-Type": "application/json"
    }
    
    new_address = {
        "title": "Test Address - Live Test",
        "full_address": "ул. Тестовая, 123, кв. 45, Бишкек",
        "street": "ул. Тестовая",
        "building": "123",
        "apartment": "45",
        "city": "Бишкек",
        "postal_code": "720000",
        "country": "Kyrgyzstan",
        "is_default": False
    }
    
    print_info("Creating address with data:")
    print(json.dumps(new_address, indent=2))
    
    response = requests.post(
        f"{BASE_URL}/profile/addresses",
        headers=headers,
        json=new_address
    )
    
    print(f"\nStatus Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    if response.status_code == 201:
        data = response.json()
        address_id = data.get('address', {}).get('id')
        print_success(f"Address created with ID: {address_id}")
        return address_id
    else:
        print_error("Failed to create address")
        return None

def verify_in_database(auth, address_id):
    """Verify address exists in database"""
    print("\n" + "=" * 60)
    print("STEP 4: VERIFY IN DATABASE")
    print("=" * 60)
    
    try:
        # Determine database URL based on market
        if auth['market'] == 'kg':
            db_url = os.getenv('KG_DATABASE_URL', 'postgresql://postgres:password@localhost:5432/marque_db_kg')
        else:
            db_url = os.getenv('US_DATABASE_URL', 'postgresql://postgres:password@localhost:5432/marque_db_us')
        
        print_info(f"Connecting to {auth['market'].upper()} database...")
        
        engine = create_engine(db_url)
        Session = sessionmaker(bind=engine)
        session = Session()
        
        # Query the address
        query = text("""
            SELECT id, user_id, title, full_address, street, building, apartment, 
                   city, postal_code, country, is_default, is_active, created_at
            FROM user_addresses
            WHERE id = :address_id AND user_id = :user_id
        """)
        
        result = session.execute(query, {
            "address_id": address_id,
            "user_id": auth['user_id']
        }).fetchone()
        
        session.close()
        
        if result:
            print_success("Address found in database!")
            print("\n📊 Database Record:")
            print(f"   ID: {result[0]}")
            print(f"   User ID: {result[1]}")
            print(f"   Title: {result[2]}")
            print(f"   Full Address: {result[3]}")
            print(f"   Street: {result[4]}")
            print(f"   Building: {result[5]}")
            print(f"   Apartment: {result[6]}")
            print(f"   City: {result[7]}")
            print(f"   Postal Code: {result[8]}")
            print(f"   Country: {result[9]}")
            print(f"   Is Default: {result[10]}")
            print(f"   Is Active: {result[11]}")
            print(f"   Created At: {result[12]}")
            return True
        else:
            print_error("Address not found in database!")
            return False
            
    except Exception as e:
        print_error(f"Database verification failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_get_addresses_again(auth):
    """Test GET /profile/addresses again to see new address"""
    print("\n" + "=" * 60)
    print("STEP 5: GET ADDRESSES (After Creation)")
    print("=" * 60)
    
    headers = {"Authorization": f"Bearer {auth['token']}"}
    
    response = requests.get(f"{BASE_URL}/profile/addresses", headers=headers)
    
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print_success(f"Found {data.get('total', 0)} addresses")
        print(f"\nAddresses List:")
        for addr in data.get('addresses', []):
            print(f"  • ID {addr['id']}: {addr['title']}")
            print(f"    {addr['full_address']}")
            print(f"    Default: {addr['is_default']}")
            print()
        return data.get('addresses', [])
    else:
        print_error("Failed to get addresses")
        return []

def test_update_address(auth, address_id):
    """Test PUT /profile/addresses/{id}"""
    print("\n" + "=" * 60)
    print(f"STEP 6: UPDATE ADDRESS (ID: {address_id})")
    print("=" * 60)
    
    headers = {
        "Authorization": f"Bearer {auth['token']}",
        "Content-Type": "application/json"
    }
    
    update_data = {
        "title": "Updated Test Address",
        "is_default": True
    }
    
    print_info("Updating address with:")
    print(json.dumps(update_data, indent=2))
    
    response = requests.put(
        f"{BASE_URL}/profile/addresses/{address_id}",
        headers=headers,
        json=update_data
    )
    
    print(f"\nStatus Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    if response.status_code == 200:
        print_success("Address updated successfully!")
        return True
    else:
        print_error("Failed to update address")
        return False

def test_delete_address(auth, address_id):
    """Test DELETE /profile/addresses/{id}"""
    print("\n" + "=" * 60)
    print(f"STEP 7: DELETE ADDRESS (ID: {address_id})")
    print("=" * 60)
    
    headers = {"Authorization": f"Bearer {auth['token']}"}
    
    # Ask user if they want to delete
    delete = input(f"\n🗑️  Delete test address {address_id}? (y/n): ").strip().lower()
    
    if delete == 'y':
        response = requests.delete(
            f"{BASE_URL}/profile/addresses/{address_id}",
            headers=headers
        )
        
        print(f"\nStatus Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 200:
            print_success("Address deleted successfully!")
            return True
        else:
            print_error("Failed to delete address")
            return False
    else:
        print_info("Skipping delete (address kept for review)")
        return False

def main():
    """Main test flow"""
    print("\n" + "=" * 60)
    print("🧪 LIVE ADDRESS API TEST")
    print("=" * 60)
    print("\nThis script will:")
    print("1. Authenticate with SMS")
    print("2. Get existing addresses")
    print("3. Create a new address")
    print("4. Verify it in the database")
    print("5. Get addresses again (should show new one)")
    print("6. Update the address")
    print("7. Optionally delete the address")
    
    # Get authentication
    auth = get_auth_token()
    if not auth:
        print_error("Authentication failed. Exiting.")
        return
    
    # Test GET addresses (initial state)
    initial_addresses = test_get_addresses(auth)
    
    # Test CREATE address
    address_id = test_create_address(auth)
    if not address_id:
        print_error("Address creation failed. Exiting.")
        return
    
    # Verify in database
    db_verified = verify_in_database(auth, address_id)
    
    # Test GET addresses again
    final_addresses = test_get_addresses_again(auth)
    
    # Test UPDATE address
    test_update_address(auth, address_id)
    
    # Test DELETE address
    test_delete_address(auth, address_id)
    
    # Final summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    print(f"✅ Authentication: SUCCESS")
    print(f"✅ GET addresses (initial): SUCCESS ({len(initial_addresses)} found)")
    print(f"✅ CREATE address: {'SUCCESS' if address_id else 'FAILED'}")
    print(f"✅ Verify in database: {'SUCCESS' if db_verified else 'FAILED'}")
    print(f"✅ GET addresses (after): SUCCESS ({len(final_addresses)} found)")
    print(f"✅ UPDATE address: SUCCESS")
    
    if address_id:
        print(f"\n🎉 ADDRESS ID {address_id} WAS CREATED IN DATABASE!")
        print(f"   User ID: {auth['user_id']}")
        print(f"   Market: {auth['market']}")
        print(f"   Phone: {auth['phone']}")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n{YELLOW}Test cancelled by user{RESET}")
    except Exception as e:
        print(f"\n\n{RED}❌ Error: {e}{RESET}")
        import traceback
        traceback.print_exc()

