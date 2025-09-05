#!/usr/bin/env python3
"""
UA and IP Validation Test Script

Tests User Agent and IP validation logic to ensure production authentication works correctly.
"""

import json
import sys
from urllib.parse import urljoin

import requests


class AuthValidationTester:
    def __init__(self, base_url="https://authz.educationhub.io"):
        self.base_url = base_url
        self.session = requests.Session()

    def test_ip_detection(self):
        """Test IP detection with various proxy headers."""
        print("🌐 Testing IP Detection...")

        # Test with different IP headers
        test_cases = [
            {"HTTP_X_FORWARDED_FOR": "203.0.113.1, 10.0.0.1, 192.168.1.1"},
            {"HTTP_X_REAL_IP": "203.0.113.2"},
            {"HTTP_CF_CONNECTING_IP": "203.0.113.3"},
            {"HTTP_TRUE_CLIENT_IP": "203.0.113.4"},
            {"REMOTE_ADDR": "203.0.113.5"},
        ]

        for i, headers in enumerate(test_cases):
            try:
                # Use debug endpoint to test IP detection
                response = self.session.get(
                    urljoin(self.base_url, "/api/v1/debug/ip/"),
                    headers=headers,
                    timeout=10
                )
                print(f"   Test {i+1}: {headers} -> {response.status_code}")
                if response.status_code == 200:
                    data = response.json()
                    print(
                        f"      Detected IP: {data.get('detected_ip', 'N/A')}")
            except Exception as e:
                print(f"   Test {i+1}: Failed - {e}")

    def test_ua_normalization(self):
        """Test User Agent normalization logic."""
        print("🖥️  Testing UA Normalization...")

        test_uas = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        ]

        for i, ua in enumerate(test_uas):
            # Test UA normalization logic locally
            import re
            normalized = re.sub(r'(\d+\.\d+)\.\d+(\.\d+)*', r'\1', ua)
            normalized = re.sub(r'\s+\(.*?\)', '', normalized)
            print(f"   Test {i+1}: {ua[:50]}...")
            print(f"      Normalized: {normalized[:50]}...")

    def test_session_flexibility(self):
        """Test session security flexibility."""
        print("🔒 Testing Session Security...")

        # This would require actual authentication flow
        print("   Note: Full session security testing requires authenticated session")
        print("   Monitor logs during production testing for session security events")

    def test_jwt_validation(self):
        """Test JWT token validation logic."""
        print("🎫 Testing JWT Validation...")

        try:
            # Test auth status endpoint
            response = self.session.get(
                urljoin(self.base_url, "/api/v1/auth-status/"),
                timeout=10
            )
            print(f"   Auth status endpoint: {response.status_code}")

            if response.status_code == 401:
                print("   ✅ Correctly returns 401 for unauthenticated request")
            elif response.status_code == 200:
                print("   ⚠️  Returns 200 - may indicate authentication bypass")
            else:
                print(f"   ❓ Unexpected status: {response.status_code}")

        except Exception as e:
            print(f"   ❌ JWT validation test failed: {e}")

    def run_all_tests(self):
        """Run all validation tests."""
        print("🧪 Starting UA and IP Validation Tests")
        print("=" * 50)

        self.test_ip_detection()
        print()
        self.test_ua_normalization()
        print()
        self.test_session_flexibility()
        print()
        self.test_jwt_validation()

        print("\n✅ Validation tests completed")
        print("\n📋 Recommendations:")
        print("   1. Monitor authentication logs during production testing")
        print("   2. Test login flow with different browsers/devices")
        print("   3. Verify session persistence across network changes")
        print("   4. Check that legitimate users aren't being logged out")


if __name__ == "__main__":
    # Allow custom base URL
    base_url = sys.argv[1] if len(
        sys.argv) > 1 else "https://authz.educationhub.io"

    tester = AuthValidationTester(base_url)
    tester.run_all_tests()
