#!/usr/bin/env python3
"""
Railway Deployment Script for Marque API
Automated deployment preparation and testing
"""

import os
import subprocess
import json
import requests
import time
from datetime import datetime

def print_section(title):
    """Print a formatted section header"""
    print(f"\n{'='*60}")
    print(f"🚀 {title}")
    print(f"{'='*60}")

def print_step(step, description):
    """Print a formatted step"""
    print(f"\n📋 Step {step}: {description}")
    print("-" * 40)

def check_railway_cli():
    """Check if Railway CLI is installed"""
    try:
        result = subprocess.run(['railway', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Railway CLI installed: {result.stdout.strip()}")
            return True
        else:
            print("❌ Railway CLI not found")
            return False
    except FileNotFoundError:
        print("❌ Railway CLI not installed")
        return False

def install_railway_cli():
    """Install Railway CLI"""
    print("📦 Installing Railway CLI...")
    try:
        # Install via npm (most common method)
        subprocess.run(['npm', 'install', '-g', '@railway/cli'], check=True)
        print("✅ Railway CLI installed successfully")
        return True
    except subprocess.CalledProcessError:
        print("❌ Failed to install Railway CLI")
        print("💡 Please install manually: https://docs.railway.app/develop/cli")
        return False

def check_git_repo():
    """Check if this is a git repository"""
    try:
        result = subprocess.run(['git', 'status'], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Git repository detected")
            return True
        else:
            print("❌ Not a git repository")
            return False
    except FileNotFoundError:
        print("❌ Git not installed")
        return False

def check_required_files():
    """Check if all required files exist"""
    required_files = [
        'marque_api_production.py',
        'railway.json',
        'Procfile',
        'runtime.txt',
        'requirements_production.txt'
    ]
    
    missing_files = []
    for file in required_files:
        if os.path.exists(file):
            print(f"✅ {file}")
        else:
            print(f"❌ {file} - MISSING")
            missing_files.append(file)
    
    return len(missing_files) == 0, missing_files

def create_env_template():
    """Create environment variables template"""
    env_template = """# Railway Environment Variables Template
# Copy these to Railway dashboard > Variables

# Twilio Configuration
TWILIO_ACCOUNT_SID=your_twilio_account_sid_here
TWILIO_AUTH_TOKEN=your_twilio_auth_token_here
TWILIO_VERIFY_SERVICE_SID=your_twilio_verify_service_sid_here

# Security (CHANGE THESE!)
SECRET_KEY=your-super-secure-production-secret-key-here
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Environment
ENVIRONMENT=production
HOST=0.0.0.0
PORT=8000

# Optional: Database URLs
# DATABASE_URL_MARQUE_KG=postgresql://user:password@host:port/db_kg
# DATABASE_URL_MARQUE_US=postgresql://user:password@host:port/db_us
"""
    
    with open('.env.railway', 'w') as f:
        f.write(env_template)
    
    print("✅ Created .env.railway template")

def test_local_api():
    """Test local API before deployment"""
    print("🧪 Testing local API...")
    
    try:
        # Test health endpoint
        response = requests.get('http://127.0.0.1:8004/health', timeout=5)
        if response.status_code == 200:
            print("✅ Local API is running and healthy")
            return True
        else:
            print(f"❌ Local API returned status {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Local API not accessible: {e}")
        print("💡 Make sure to run: python marque_api_production.py")
        return False

def deploy_to_railway():
    """Deploy to Railway"""
    print("🚀 Deploying to Railway...")
    
    try:
        # Login to Railway
        print("🔐 Logging into Railway...")
        subprocess.run(['railway', 'login'], check=True)
        
        # Link to project (or create new)
        print("🔗 Linking to Railway project...")
        subprocess.run(['railway', 'link'], check=True)
        
        # Deploy
        print("📦 Deploying...")
        subprocess.run(['railway', 'up'], check=True)
        
        print("✅ Deployment initiated!")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Deployment failed: {e}")
        return False

def get_railway_url():
    """Get Railway deployment URL"""
    try:
        result = subprocess.run(['railway', 'domain'], capture_output=True, text=True)
        if result.returncode == 0:
            domain = result.stdout.strip()
            url = f"https://{domain}"
            print(f"🌐 Your API is available at: {url}")
            return url
        else:
            print("❌ Could not get Railway URL")
            return None
    except Exception as e:
        print(f"❌ Error getting URL: {e}")
        return None

def test_deployed_api(url):
    """Test deployed API"""
    print(f"🧪 Testing deployed API at {url}...")
    
    try:
        # Test health endpoint
        response = requests.get(f"{url}/health", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print("✅ Deployed API is healthy!")
            print(f"   Service: {data.get('service', 'Unknown')}")
            print(f"   Version: {data.get('version', 'Unknown')}")
            print(f"   SMS Provider: {data.get('sms_provider', 'Unknown')}")
            return True
        else:
            print(f"❌ Deployed API returned status {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Deployed API not accessible: {e}")
        return False

def main():
    """Main deployment process"""
    print_section("Marque API Railway Deployment")
    print(f"🕐 Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Step 1: Check prerequisites
    print_step(1, "Checking Prerequisites")
    
    # Check Railway CLI
    if not check_railway_cli():
        if not install_railway_cli():
            print("❌ Cannot proceed without Railway CLI")
            return False
    
    # Check Git repository
    if not check_git_repo():
        print("❌ Please initialize git repository first:")
        print("   git init")
        print("   git add .")
        print("   git commit -m 'Initial commit'")
        return False
    
    # Step 2: Check required files
    print_step(2, "Checking Required Files")
    files_ok, missing_files = check_required_files()
    if not files_ok:
        print(f"❌ Missing files: {', '.join(missing_files)}")
        print("💡 Please create missing files before deployment")
        return False
    
    # Step 3: Create environment template
    print_step(3, "Creating Environment Template")
    create_env_template()
    
    # Step 4: Test local API
    print_step(4, "Testing Local API")
    if not test_local_api():
        print("❌ Local API test failed")
        print("💡 Please fix local API issues before deployment")
        return False
    
    # Step 5: Deploy to Railway
    print_step(5, "Deploying to Railway")
    if not deploy_to_railway():
        print("❌ Railway deployment failed")
        return False
    
    # Step 6: Test deployed API
    print_step(6, "Testing Deployed API")
    url = get_railway_url()
    if url and test_deployed_api(url):
        print_section("Deployment Complete!")
        print(f"🎉 Your Marque API is live at: {url}")
        print(f"📱 SMS verification ready for production")
        print(f"📚 API docs: {url}/docs")
        print(f"🔍 Health check: {url}/health")
        return True
    else:
        print("❌ Deployment test failed")
        return False

if __name__ == "__main__":
    success = main()
    if success:
        print("\n🎉 Railway deployment successful!")
        print("📱 Your phone authentication API is now live!")
    else:
        print("\n❌ Railway deployment failed")
        print("💡 Check the errors above and try again")
