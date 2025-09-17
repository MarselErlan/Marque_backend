#!/usr/bin/env python3
"""
SMS Configuration Diagnostic Tool
Helps diagnose why sms_configured is showing false on Railway
"""

import requests
import json
import os
from typing import Dict, Any


class SMSConfigurationDiagnostic:
    """Diagnostic tool for SMS configuration issues"""
    
    def __init__(self, base_url: str = "https://marque.website"):
        self.base_url = base_url
        self.session = requests.Session()
    
    def run_full_diagnosis(self) -> Dict[str, Any]:
        """Run complete SMS configuration diagnosis"""
        print("🔍 SMS Configuration Diagnostic Tool")
        print("=" * 60)
        
        results = {
            "health_check": self.check_health_endpoint(),
            "debug_environment": self.check_debug_environment(),
            "twilio_connectivity": self.check_twilio_connectivity(),
            "sms_functionality": self.test_sms_functionality(),
            "recommendations": []
        }
        
        self.generate_recommendations(results)
        self.print_summary(results)
        
        return results
    
    def check_health_endpoint(self) -> Dict[str, Any]:
        """Check health endpoint for SMS configuration"""
        print("\n📊 Checking Health Endpoint...")
        print("-" * 30)
        
        try:
            response = self.session.get(f"{self.base_url}/health", timeout=10)
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Health endpoint accessible")
                print(f"   Status: {data.get('status', 'unknown')}")
                print(f"   SMS Provider: {data.get('sms_provider', 'unknown')}")
                print(f"   SMS Configured: {data.get('sms_configured', 'unknown')}")
                
                return {
                    "status": "success",
                    "data": data,
                    "sms_configured": data.get('sms_configured', False)
                }
            else:
                print(f"❌ Health endpoint returned {response.status_code}")
                return {"status": "error", "code": response.status_code}
                
        except Exception as e:
            print(f"❌ Health endpoint error: {e}")
            return {"status": "error", "message": str(e)}
    
    def check_debug_environment(self) -> Dict[str, Any]:
        """Check debug environment endpoint"""
        print("\n🔍 Checking Debug Environment...")
        print("-" * 30)
        
        try:
            response = self.session.get(f"{self.base_url}/debug/env", timeout=10)
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Debug endpoint accessible")
                
                # Check each environment variable
                env_vars = {
                    "TWILIO_AVAILABLE": data.get('TWILIO_AVAILABLE'),
                    "TWILIO_READY": data.get('TWILIO_READY'),
                    "TWILIO_ACCOUNT_SID": data.get('TWILIO_ACCOUNT_SID'),
                    "TWILIO_AUTH_TOKEN": data.get('TWILIO_AUTH_TOKEN'),
                    "TWILIO_VERIFY_SERVICE_SID": data.get('TWILIO_VERIFY_SERVICE_SID')
                }
                
                for var, value in env_vars.items():
                    status = "✅ Set" if value == "✅ Set" else "❌ Missing"
                    print(f"   {var}: {status}")
                
                missing_vars = [var for var, value in env_vars.items() 
                               if value == "❌ Missing" and var != "TWILIO_AVAILABLE"]
                
                return {
                    "status": "success",
                    "data": data,
                    "missing_vars": missing_vars,
                    "twilio_ready": data.get('TWILIO_READY', False)
                }
            else:
                print(f"❌ Debug endpoint returned {response.status_code}")
                return {"status": "error", "code": response.status_code}
                
        except Exception as e:
            print(f"❌ Debug endpoint error: {e}")
            return {"status": "error", "message": str(e)}
    
    def check_twilio_connectivity(self) -> Dict[str, Any]:
        """Check Twilio API connectivity"""
        print("\n🌐 Checking Twilio Connectivity...")
        print("-" * 30)
        
        try:
            # Test basic connectivity to Twilio
            response = self.session.get("https://api.twilio.com", timeout=10)
            print(f"✅ Twilio API reachable: {response.status_code}")
            
            # Test Verify API specifically
            verify_response = self.session.get("https://verify.twilio.com", timeout=10)
            print(f"✅ Twilio Verify API reachable: {verify_response.status_code}")
            
            return {"status": "success", "connectivity": True}
            
        except Exception as e:
            print(f"❌ Twilio connectivity error: {e}")
            return {"status": "error", "message": str(e)}
    
    def test_sms_functionality(self) -> Dict[str, Any]:
        """Test SMS functionality end-to-end"""
        print("\n🧪 Testing SMS Functionality...")
        print("-" * 30)
        
        test_phone = "+13473926894"
        
        try:
            # Test phone validation
            validate_payload = {"phone": test_phone}
            validate_response = self.session.post(
                f"{self.base_url}/api/v1/validate-phone",
                json=validate_payload,
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            
            if validate_response.status_code != 200:
                print(f"❌ Phone validation failed: {validate_response.status_code}")
                return {"status": "error", "step": "validation"}
            
            print("✅ Phone validation: PASSED")
            
            # Test send verification
            send_payload = {"phone": test_phone}
            send_response = self.session.post(
                f"{self.base_url}/api/v1/auth/send-verification",
                json=send_payload,
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            
            if send_response.status_code != 200:
                print(f"❌ Send verification failed: {send_response.status_code}")
                return {"status": "error", "step": "send_verification"}
            
            send_data = send_response.json()
            print(f"✅ Send verification: PASSED ({send_data.get('message', '')})")
            
            # Test verify code (demo mode)
            verify_payload = {
                "phone": test_phone,
                "code": "123456"  # Demo code
            }
            verify_response = self.session.post(
                f"{self.base_url}/api/v1/auth/verify-code",
                json=verify_payload,
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            
            if verify_response.status_code != 200:
                print(f"❌ Verify code failed: {verify_response.status_code}")
                return {"status": "error", "step": "verify_code"}
            
            verify_data = verify_response.json()
            print(f"✅ Verify code: PASSED")
            
            return {
                "status": "success",
                "demo_mode_working": True,
                "has_token": "access_token" in verify_data
            }
            
        except Exception as e:
            print(f"❌ SMS functionality error: {e}")
            return {"status": "error", "message": str(e)}
    
    def generate_recommendations(self, results: Dict[str, Any]):
        """Generate recommendations based on diagnosis results"""
        print("\n💡 Generating Recommendations...")
        print("-" * 30)
        
        recommendations = []
        
        # Check if SMS is configured
        health_data = results.get("health_check", {})
        if health_data.get("status") == "success":
            if not health_data.get("sms_configured", False):
                recommendations.append({
                    "issue": "SMS not configured",
                    "solution": "Add Twilio environment variables to Railway dashboard",
                    "priority": "high"
                })
        
        # Check missing environment variables
        debug_data = results.get("debug_environment", {})
        if debug_data.get("status") == "success":
            missing_vars = debug_data.get("missing_vars", [])
            if missing_vars:
                recommendations.append({
                    "issue": f"Missing environment variables: {', '.join(missing_vars)}",
                    "solution": "Add these variables to Railway dashboard > Variables",
                    "priority": "high"
                })
        
        # Check Twilio connectivity
        twilio_data = results.get("twilio_connectivity", {})
        if twilio_data.get("status") != "success":
            recommendations.append({
                "issue": "Twilio API not reachable",
                "solution": "Check network connectivity and Twilio service status",
                "priority": "medium"
            })
        
        # Check if demo mode is working
        sms_data = results.get("sms_functionality", {})
        if sms_data.get("status") == "success" and sms_data.get("demo_mode_working"):
            recommendations.append({
                "issue": "Demo mode working but SMS not configured",
                "solution": "Configure Twilio credentials for production SMS",
                "priority": "medium"
            })
        
        results["recommendations"] = recommendations
        
        for i, rec in enumerate(recommendations, 1):
            priority_emoji = "🔴" if rec["priority"] == "high" else "🟡"
            print(f"{priority_emoji} {i}. {rec['issue']}")
            print(f"   Solution: {rec['solution']}")
    
    def print_summary(self, results: Dict[str, Any]):
        """Print diagnosis summary"""
        print("\n📋 DIAGNOSIS SUMMARY")
        print("=" * 60)
        
        # Overall status
        health_ok = results["health_check"].get("status") == "success"
        debug_ok = results["debug_environment"].get("status") == "success"
        sms_working = results["sms_functionality"].get("status") == "success"
        
        if health_ok and debug_ok and sms_working:
            print("✅ Overall Status: SYSTEM FUNCTIONAL")
            print("   - API is accessible")
            print("   - Demo mode is working")
            print("   - SMS functionality is operational")
        else:
            print("❌ Overall Status: ISSUES DETECTED")
            if not health_ok:
                print("   - Health endpoint issues")
            if not debug_ok:
                print("   - Debug endpoint issues")
            if not sms_working:
                print("   - SMS functionality issues")
        
        # SMS Configuration Status
        sms_configured = results["health_check"].get("data", {}).get("sms_configured", False)
        if sms_configured:
            print("✅ SMS Configuration: PROPERLY CONFIGURED")
        else:
            print("❌ SMS Configuration: NOT CONFIGURED (Running in demo mode)")
        
        # Recommendations count
        rec_count = len(results["recommendations"])
        if rec_count > 0:
            print(f"💡 {rec_count} recommendation(s) provided above")
        else:
            print("🎉 No issues found - system is working correctly!")


def main():
    """Main diagnostic function"""
    diagnostic = SMSConfigurationDiagnostic()
    results = diagnostic.run_full_diagnosis()
    
    # Return exit code based on results
    health_ok = results["health_check"].get("status") == "success"
    sms_working = results["sms_functionality"].get("status") == "success"
    
    if health_ok and sms_working:
        print("\n🎉 Diagnostic completed successfully!")
        return 0
    else:
        print("\n⚠️  Diagnostic found issues that need attention.")
        return 1


if __name__ == "__main__":
    exit_code = main()
    exit(exit_code)
