#!/usr/bin/env python3
"""
E-Connect Backend API Test Suite
Comprehensive testing for all backend endpoints before deployment
"""

import requests
import json
import time
import sys
from datetime import datetime, timedelta
import pytz

# Configuration
BASE_URL = "http://localhost:8000"
IST = pytz.timezone("Asia/Kolkata")

class Colors:
    """ANSI color codes for terminal output"""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    END = '\033[0m'

class TestReporter:
    """Test result reporter"""
    def __init__(self):
        self.total_tests = 0
        self.passed_tests = 0
        self.failed_tests = 0
        self.warnings = 0
        self.results = []

    def log_test(self, test_name, status, message="", response_time=None):
        self.total_tests += 1
        if status == "PASS":
            self.passed_tests += 1
            icon = "✅"
            color = Colors.GREEN
        elif status == "FAIL":
            self.failed_tests += 1
            icon = "❌"
            color = Colors.RED
        else:  # WARNING
            self.warnings += 1
            icon = "⚠️"
            color = Colors.YELLOW

        time_str = f" ({response_time:.2f}ms)" if response_time else ""
        print(f"{color}{icon} {test_name}{time_str}{Colors.END}")
        if message:
            print(f"   {message}")
        
        self.results.append({
            "test": test_name,
            "status": status,
            "message": message,
            "response_time": response_time,
            "timestamp": datetime.now(IST).isoformat()
        })

    def print_summary(self):
        print(f"\n{Colors.BOLD}=== TEST SUMMARY ==={Colors.END}")
        print(f"Total Tests: {self.total_tests}")
        print(f"{Colors.GREEN}Passed: {self.passed_tests}{Colors.END}")
        print(f"{Colors.RED}Failed: {self.failed_tests}{Colors.END}")
        print(f"{Colors.YELLOW}Warnings: {self.warnings}{Colors.END}")
        
        success_rate = (self.passed_tests / self.total_tests * 100) if self.total_tests > 0 else 0
        print(f"Success Rate: {success_rate:.1f}%")
        
        if success_rate >= 90:
            print(f"{Colors.GREEN}🎉 DEPLOYMENT READY!{Colors.END}")
        elif success_rate >= 75:
            print(f"{Colors.YELLOW}⚠️ NEEDS ATTENTION BEFORE DEPLOYMENT{Colors.END}")
        else:
            print(f"{Colors.RED}🚨 NOT READY FOR DEPLOYMENT{Colors.END}")

    def save_report(self, filename="test_report.json"):
        report = {
            "summary": {
                "total_tests": self.total_tests,
                "passed": self.passed_tests,
                "failed": self.failed_tests,
                "warnings": self.warnings,
                "success_rate": (self.passed_tests / self.total_tests * 100) if self.total_tests > 0 else 0,
                "timestamp": datetime.now(IST).isoformat()
            },
            "results": self.results
        }
        
        with open(filename, 'w') as f:
            json.dump(report, f, indent=2)
        print(f"\n📊 Test report saved to {filename}")

class EConnectAPITester:
    """Main test class for E-Connect API testing"""
    
    def __init__(self):
        self.reporter = TestReporter()
        self.auth_token = None
        self.test_user_id = None
        self.session = requests.Session()

    def test_connection(self):
        """Test basic server connectivity"""
        try:
            start_time = time.time()
            response = self.session.get(f"{BASE_URL}/test", timeout=5)
            response_time = (time.time() - start_time) * 1000
            
            if response.status_code == 200 and "Backend is connected" in response.text:
                self.reporter.log_test("Server Connectivity", "PASS", 
                                     "Backend server is running", response_time)
                return True
            else:
                self.reporter.log_test("Server Connectivity", "FAIL", 
                                     f"Unexpected response: {response.text}")
                return False
        except Exception as e:
            self.reporter.log_test("Server Connectivity", "FAIL", f"Connection error: {str(e)}")
            return False

    def test_root_endpoint(self):
        """Test root endpoint"""
        try:
            start_time = time.time()
            response = self.session.get(f"{BASE_URL}/", timeout=5)
            response_time = (time.time() - start_time) * 1000
            
            if response.status_code == 200:
                data = response.json()
                if "Hello" in data and data["Hello"] == "World":
                    self.reporter.log_test("Root Endpoint", "PASS", 
                                         "Root endpoint responding correctly", response_time)
                else:
                    self.reporter.log_test("Root Endpoint", "WARNING", 
                                         f"Unexpected response format: {data}")
            else:
                self.reporter.log_test("Root Endpoint", "FAIL", 
                                     f"Status code: {response.status_code}")
        except Exception as e:
            self.reporter.log_test("Root Endpoint", "FAIL", f"Error: {str(e)}")

    def test_notification_test_endpoint(self):
        """Test notification test endpoint"""
        try:
            # Use a test user ID
            test_userid = "test_user_123"
            start_time = time.time()
            response = self.session.get(f"{BASE_URL}/test-notifications/{test_userid}", timeout=10)
            response_time = (time.time() - start_time) * 1000
            
            if response.status_code == 200:
                data = response.json()
                if "status" in data and "Test notification created" in data["status"]:
                    self.reporter.log_test("Notification Test Endpoint", "PASS", 
                                         "Test notification created successfully", response_time)
                else:
                    self.reporter.log_test("Notification Test Endpoint", "WARNING", 
                                         f"Unexpected response: {data}")
            else:
                self.reporter.log_test("Notification Test Endpoint", "FAIL", 
                                     f"Status code: {response.status_code}")
        except Exception as e:
            self.reporter.log_test("Notification Test Endpoint", "FAIL", f"Error: {str(e)}")

    def test_attendance_test_endpoint(self):
        """Test attendance notification test endpoint"""
        try:
            start_time = time.time()
            response = self.session.post(f"{BASE_URL}/test-attendance-notification", timeout=10)
            response_time = (time.time() - start_time) * 1000
            
            if response.status_code == 200:
                data = response.json()
                if "message" in data:
                    self.reporter.log_test("Attendance Test Endpoint", "PASS", 
                                         data["message"], response_time)
                else:
                    self.reporter.log_test("Attendance Test Endpoint", "WARNING", 
                                         f"Unexpected response: {data}")
            else:
                self.reporter.log_test("Attendance Test Endpoint", "FAIL", 
                                     f"Status code: {response.status_code}")
        except Exception as e:
            self.reporter.log_test("Attendance Test Endpoint", "FAIL", f"Error: {str(e)}")

    def test_user_signup(self):
        """Test user signup functionality"""
        try:
            test_user = {
                "email": f"test_{int(time.time())}@econnect.com",
                "password": "TestPassword123!",
                "name": "Test User"
            }
            
            start_time = time.time()
            response = self.session.post(f"{BASE_URL}/signup", json=test_user, timeout=10)
            response_time = (time.time() - start_time) * 1000
            
            if response.status_code == 200:
                data = response.json()
                if "access_token" in data:
                    self.reporter.log_test("User Signup", "PASS", 
                                         "User created successfully with JWT token", response_time)
                    return True
                else:
                    self.reporter.log_test("User Signup", "WARNING", 
                                         f"Signup successful but unexpected response: {data}")
            else:
                self.reporter.log_test("User Signup", "FAIL", 
                                     f"Status code: {response.status_code}, Response: {response.text}")
                return False
        except Exception as e:
            self.reporter.log_test("User Signup", "FAIL", f"Error: {str(e)}")
            return False

    def test_user_signin(self):
        """Test user signin functionality"""
        try:
            # First create a test user
            test_user = {
                "email": f"signin_test_{int(time.time())}@econnect.com", 
                "password": "TestPassword123!",
                "name": "Signin Test User"
            }
            
            # Signup first
            signup_response = self.session.post(f"{BASE_URL}/signup", json=test_user, timeout=10)
            if signup_response.status_code != 200:
                self.reporter.log_test("User Signin (Setup)", "FAIL", "Could not create test user for signin test")
                return False
            
            # Now test signin
            signin_data = {
                "email": test_user["email"],
                "password": test_user["password"]
            }
            
            start_time = time.time()
            response = self.session.post(f"{BASE_URL}/signin", json=signin_data, timeout=10)
            response_time = (time.time() - start_time) * 1000
            
            if response.status_code == 200:
                data = response.json()
                if "jwt" in data and "Details" in data:
                    self.auth_token = data["jwt"]["access_token"]
                    self.reporter.log_test("User Signin", "PASS", 
                                         "User signin successful with JWT", response_time)
                    return True
                else:
                    self.reporter.log_test("User Signin", "WARNING", 
                                         f"Signin successful but unexpected response format: {data}")
            else:
                self.reporter.log_test("User Signin", "FAIL", 
                                     f"Status code: {response.status_code}, Response: {response.text}")
                return False
        except Exception as e:
            self.reporter.log_test("User Signin", "FAIL", f"Error: {str(e)}")
            return False

    def test_protected_endpoint(self):
        """Test protected endpoint with JWT"""
        if not self.auth_token:
            self.reporter.log_test("Protected Endpoint", "FAIL", "No auth token available")
            return False
            
        try:
            headers = {"Authorization": f"Bearer {self.auth_token}"}
            test_data = {"id": "test_id_123"}
            
            start_time = time.time()
            response = self.session.post(f"{BASE_URL}/id", json=test_data, headers=headers, timeout=10)
            response_time = (time.time() - start_time) * 1000
            
            if response.status_code == 200:
                self.reporter.log_test("Protected Endpoint", "PASS", 
                                     "JWT authentication working", response_time)
                return True
            else:
                self.reporter.log_test("Protected Endpoint", "FAIL", 
                                     f"Status code: {response.status_code}")
                return False
        except Exception as e:
            self.reporter.log_test("Protected Endpoint", "FAIL", f"Error: {str(e)}")
            return False

    def test_clock_endpoints(self):
        """Test clock-in and clock-out endpoints"""
        try:
            # Test clock-in
            clock_data = {
                "userid": "test_user_123",
                "name": "Test User",
                "current_time": datetime.now(IST).strftime("%Y-%m-%d %H:%M:%S")
            }
            
            start_time = time.time()
            response = self.session.post(f"{BASE_URL}/Clockin", json=clock_data, timeout=10)
            response_time = (time.time() - start_time) * 1000
            
            if response.status_code == 200:
                data = response.json()
                if "message" in data:
                    self.reporter.log_test("Clock-in Endpoint", "PASS", 
                                         f"Clock-in response: {data['message']}", response_time)
                else:
                    self.reporter.log_test("Clock-in Endpoint", "WARNING", 
                                         f"Unexpected response: {data}")
            else:
                self.reporter.log_test("Clock-in Endpoint", "FAIL", 
                                     f"Status code: {response.status_code}")
            
            # Test clock-out
            start_time = time.time()
            response = self.session.post(f"{BASE_URL}/Clockout", json=clock_data, timeout=10)
            response_time = (time.time() - start_time) * 1000
            
            if response.status_code == 200:
                data = response.json()
                if "message" in data:
                    self.reporter.log_test("Clock-out Endpoint", "PASS", 
                                         f"Clock-out response: {data['message']}", response_time)
                else:
                    self.reporter.log_test("Clock-out Endpoint", "WARNING", 
                                         f"Unexpected response: {data}")
            else:
                self.reporter.log_test("Clock-out Endpoint", "FAIL", 
                                     f"Status code: {response.status_code}")
                
        except Exception as e:
            self.reporter.log_test("Clock Endpoints", "FAIL", f"Error: {str(e)}")

    def test_leave_request_endpoint(self):
        """Test leave request endpoint"""
        try:
            leave_data = {
                "userid": "test_user_123",
                "employeeName": "Test User",
                "leaveType": "Sick Leave",
                "selectedDate": (datetime.now() + timedelta(days=7)).strftime("%d-%m-%Y"),
                "requestDate": datetime.now().strftime("%d-%m-%Y"),
                "reason": "Test leave request for API testing"
            }
            
            start_time = time.time()
            response = self.session.post(f"{BASE_URL}/leave-request", json=leave_data, timeout=10)
            response_time = (time.time() - start_time) * 1000
            
            if response.status_code == 200:
                data = response.json()
                if "success" in data or "message" in data:
                    self.reporter.log_test("Leave Request Endpoint", "PASS", 
                                         "Leave request processed", response_time)
                else:
                    self.reporter.log_test("Leave Request Endpoint", "WARNING", 
                                         f"Unexpected response: {data}")
            else:
                self.reporter.log_test("Leave Request Endpoint", "FAIL", 
                                     f"Status code: {response.status_code}")
                
        except Exception as e:
            self.reporter.log_test("Leave Request Endpoint", "FAIL", f"Error: {str(e)}")

    def test_database_connectivity(self):
        """Test MongoDB connectivity"""
        try:
            from pymongo import MongoClient
            
            start_time = time.time()
            client = MongoClient("mongodb://localhost:27017", serverSelectionTimeoutMS=5000)
            result = client.admin.command('ping')
            response_time = (time.time() - start_time) * 1000
            
            if result.get('ok') == 1.0:
                # Test database and collections
                db = client["RBG_AI"]
                collections = db.list_collection_names()
                expected_collections = ["Users", "Attendance", "Leave_Details", "RemoteWork", "tasks", "notifications"]
                
                missing_collections = [col for col in expected_collections if col not in collections]
                
                if not missing_collections:
                    self.reporter.log_test("Database Connectivity", "PASS", 
                                         f"MongoDB connected, all collections present", response_time)
                else:
                    self.reporter.log_test("Database Connectivity", "WARNING", 
                                         f"MongoDB connected but missing collections: {missing_collections}")
            else:
                self.reporter.log_test("Database Connectivity", "FAIL", "MongoDB ping failed")
                
        except Exception as e:
            self.reporter.log_test("Database Connectivity", "FAIL", f"Error: {str(e)}")

    def test_notification_endpoints(self):
        """Test notification system endpoints"""
        test_userid = "test_user_123"
        
        try:
            # Test get notifications
            start_time = time.time()
            response = self.session.get(f"{BASE_URL}/notifications/{test_userid}", timeout=10)
            response_time = (time.time() - start_time) * 1000
            
            if response.status_code == 200:
                self.reporter.log_test("Get Notifications", "PASS", 
                                     "Notifications endpoint responding", response_time)
            else:
                self.reporter.log_test("Get Notifications", "FAIL", 
                                     f"Status code: {response.status_code}")
            
            # Test unread count
            start_time = time.time()
            response = self.session.get(f"{BASE_URL}/notifications/{test_userid}/unread-count", timeout=10)
            response_time = (time.time() - start_time) * 1000
            
            if response.status_code == 200:
                data = response.json()
                if "unread_count" in data:
                    self.reporter.log_test("Unread Count", "PASS", 
                                         f"Unread count: {data['unread_count']}", response_time)
                else:
                    self.reporter.log_test("Unread Count", "WARNING", 
                                         f"Unexpected response: {data}")
            else:
                self.reporter.log_test("Unread Count", "FAIL", 
                                     f"Status code: {response.status_code}")
                
        except Exception as e:
            self.reporter.log_test("Notification Endpoints", "FAIL", f"Error: {str(e)}")

    def run_all_tests(self):
        """Run all test suites"""
        print(f"{Colors.BOLD}{Colors.BLUE}🧪 E-Connect Backend API Test Suite{Colors.END}")
        print(f"Testing against: {BASE_URL}")
        print(f"Timestamp: {datetime.now(IST).strftime('%Y-%m-%d %H:%M:%S IST')}")
        print("=" * 60)
        
        # Core connectivity tests
        print(f"\n{Colors.CYAN}📡 Testing Core Connectivity{Colors.END}")
        if not self.test_connection():
            print(f"{Colors.RED}❌ Server not reachable. Stopping tests.{Colors.END}")
            return
        
        self.test_root_endpoint()
        self.test_database_connectivity()
        
        # Authentication tests
        print(f"\n{Colors.CYAN}🔐 Testing Authentication{Colors.END}")
        self.test_user_signup()
        self.test_user_signin()
        self.test_protected_endpoint()
        
        # Core feature tests
        print(f"\n{Colors.CYAN}⏰ Testing Attendance System{Colors.END}")
        self.test_clock_endpoints()
        
        print(f"\n{Colors.CYAN}🏖️ Testing Leave Management{Colors.END}")
        self.test_leave_request_endpoint()
        
        print(f"\n{Colors.CYAN}🔔 Testing Notification System{Colors.END}")
        self.test_notification_test_endpoint()
        self.test_attendance_test_endpoint()
        self.test_notification_endpoints()
        
        # Print summary
        self.reporter.print_summary()
        self.reporter.save_report("backend_test_report.json")

def main():
    """Main function to run tests"""
    print(f"{Colors.PURPLE}Starting E-Connect Backend API Tests...{Colors.END}")
    
    tester = EConnectAPITester()
    tester.run_all_tests()
    
    print(f"\n{Colors.BLUE}Test execution completed!{Colors.END}")
    print(f"Check 'backend_test_report.json' for detailed results.")

if __name__ == "__main__":
    main()
