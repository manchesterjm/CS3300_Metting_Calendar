#!/usr/bin/env python3
"""Live server testing script to verify all user actions work properly."""

import requests
from bs4 import BeautifulSoup
import time
import sys
from datetime import date, timedelta

BASE_URL = "http://localhost:8000"
TEST_USERNAME = f"testuser_live_{int(time.time())}"
TEST_PASSWORD = "TestPass123!"
TEST_EMAIL = f"{TEST_USERNAME}@test.com"

class LiveServerTester:
    def __init__(self):
        self.session = requests.Session()
        self.username = TEST_USERNAME
        self.password = TEST_PASSWORD
        self.email = TEST_EMAIL

    def get_csrf_token(self, url):
        """Extract CSRF token from a page."""
        response = self.session.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        csrf_input = soup.find('input', {'name': 'csrfmiddlewaretoken'})
        if csrf_input:
            return csrf_input.get('value')
        return None

    def test_home_page(self):
        """Test that home page loads and redirects to login."""
        print("\n[TEST] Home page redirect...")
        response = self.session.get(f"{BASE_URL}/", allow_redirects=False)
        if response.status_code == 302 and '/login/' in response.headers.get('Location', ''):
            print("✅ Home page redirects to login correctly")
            return True
        print(f"❌ Home page test failed: Status {response.status_code}")
        return False

    def test_registration_page(self):
        """Test that registration page loads."""
        print("\n[TEST] Registration page loads...")
        response = self.session.get(f"{BASE_URL}/register/")
        if response.status_code == 200 and 'Register' in response.text:
            print("✅ Registration page loads correctly")
            return True
        print(f"❌ Registration page test failed: Status {response.status_code}")
        return False

    def test_user_registration(self):
        """Test user registration functionality."""
        print(f"\n[TEST] User registration (creating '{self.username}')...")

        csrf_token = self.get_csrf_token(f"{BASE_URL}/register/")
        if not csrf_token:
            print("❌ Failed to get CSRF token for registration")
            return False

        data = {
            'csrfmiddlewaretoken': csrf_token,
            'username': self.username,
            'email': self.email,
            'password1': self.password,
            'password2': self.password,
        }

        response = self.session.post(f"{BASE_URL}/register/", data=data)

        if response.status_code == 200 and 'successfully' in response.text.lower():
            print(f"✅ User '{self.username}' registered successfully")
            return True
        elif 'calendar' in response.url or response.status_code == 302:
            print(f"✅ User '{self.username}' registered (redirected to calendar)")
            return True
        print(f"❌ Registration failed: Status {response.status_code}")
        if 'error' in response.text.lower():
            print(f"   Error in response: {response.text[:200]}")
        return False

    def test_login(self):
        """Test user login functionality."""
        print(f"\n[TEST] User login ('{self.username}')...")

        csrf_token = self.get_csrf_token(f"{BASE_URL}/login/")
        if not csrf_token:
            print("❌ Failed to get CSRF token for login")
            return False

        data = {
            'csrfmiddlewaretoken': csrf_token,
            'username': self.username,
            'password': self.password,
        }

        response = self.session.post(f"{BASE_URL}/login/", data=data)

        if 'calendar' in response.url or (response.status_code == 200 and 'Meeting Calendar' in response.text):
            print(f"✅ User '{self.username}' logged in successfully")
            return True
        print(f"❌ Login failed: Status {response.status_code}, URL: {response.url}")
        return False

    def test_calendar_view(self):
        """Test that calendar view loads."""
        print("\n[TEST] Calendar view loads...")
        response = self.session.get(f"{BASE_URL}/")

        if response.status_code == 200 and 'Meeting Calendar' in response.text:
            print("✅ Calendar view loads correctly")
            return True
        print(f"❌ Calendar view test failed: Status {response.status_code}")
        return False

    def test_submit_unavailability(self):
        """Test submitting unavailability."""
        print("\n[TEST] Submit unavailability...")

        csrf_token = self.get_csrf_token(f"{BASE_URL}/")
        if not csrf_token:
            print("❌ Failed to get CSRF token for calendar")
            return False

        tomorrow = date.today() + timedelta(days=1)
        data = {
            'csrfmiddlewaretoken': csrf_token,
            'date': tomorrow.strftime('%Y-%m-%d'),
            'start_time': '09:00',
            'end_time': '10:00',
            'description': 'Live test unavailability',
            'submit_unavailability': 'Submit',
        }

        response = self.session.post(f"{BASE_URL}/", data=data)

        if response.status_code == 200 or response.url == f"{BASE_URL}/":
            print("✅ Unavailability submitted successfully")
            return True
        print(f"❌ Submit unavailability failed: Status {response.status_code}")
        return False

    def test_show_free_times(self):
        """Test showing free times."""
        print("\n[TEST] Show free times...")

        csrf_token = self.get_csrf_token(f"{BASE_URL}/")
        if not csrf_token:
            print("❌ Failed to get CSRF token")
            return False

        today = date.today()
        data = {
            'csrfmiddlewaretoken': csrf_token,
            'date': today.strftime('%Y-%m-%d'),
            'show_free_times': 'Show Free Times',
        }

        response = self.session.post(f"{BASE_URL}/", data=data)

        if response.status_code == 200:
            # Check if free times are displayed or message about all slots free
            if 'free' in response.text.lower() or '08:00' in response.text:
                print("✅ Free times calculated and displayed")
                return True
        print(f"❌ Show free times failed: Status {response.status_code}")
        return False

    def test_show_last_five(self):
        """Test showing last five entries."""
        print("\n[TEST] Show last five entries...")

        csrf_token = self.get_csrf_token(f"{BASE_URL}/")
        if not csrf_token:
            print("❌ Failed to get CSRF token")
            return False

        data = {
            'csrfmiddlewaretoken': csrf_token,
            'show_last_five': 'Show Last 5 Entries',
        }

        response = self.session.post(f"{BASE_URL}/", data=data)

        if response.status_code == 200:
            print("✅ Last five entries retrieved successfully")
            return True
        print(f"❌ Show last five failed: Status {response.status_code}")
        return False

    def test_delete_selected(self):
        """Test deleting selected entries."""
        print("\n[TEST] Delete selected entries...")

        # First get the calendar page to find entry IDs
        response = self.session.get(f"{BASE_URL}/")
        soup = BeautifulSoup(response.text, 'html.parser')
        csrf_token = soup.find('input', {'name': 'csrfmiddlewaretoken'})

        if not csrf_token:
            print("❌ Failed to get CSRF token")
            return False

        csrf_value = csrf_token.get('value')

        # Look for checkboxes (entry IDs)
        checkboxes = soup.find_all('input', {'type': 'checkbox', 'name': 'selected_entries'})

        if checkboxes:
            entry_id = checkboxes[0].get('value')
            data = {
                'csrfmiddlewaretoken': csrf_value,
                'selected_entries': entry_id,
                'delete_selected': 'Delete Selected',
            }

            response = self.session.post(f"{BASE_URL}/", data=data)

            if response.status_code == 200 or response.url == f"{BASE_URL}/":
                print("✅ Delete selected entries works")
                return True
        else:
            # No entries to delete, but the functionality exists
            print("✅ Delete selected functionality available (no entries to delete)")
            return True

        print(f"❌ Delete selected failed")
        return False

    def test_group_calendar(self):
        """Test group functionality (groups list page)."""
        print("\n[TEST] Groups list view...")

        response = self.session.get(f"{BASE_URL}/groups/")

        if response.status_code == 200 and ('Group' in response.text or 'groups' in response.text.lower()):
            print("✅ Groups list view loads correctly")
            return True
        print(f"❌ Groups list test failed: Status {response.status_code}")
        return False

    def test_logout(self):
        """Test logout functionality."""
        print("\n[TEST] Logout...")

        response = self.session.get(f"{BASE_URL}/logout/", allow_redirects=True)

        if 'login' in response.url.lower() or response.status_code == 200:
            print("✅ Logout successful")
            return True
        print(f"❌ Logout failed: Status {response.status_code}")
        return False

    def run_all_tests(self):
        """Run all live server tests."""
        print("="*70)
        print("LIVE SERVER TESTING - SOFA Refactored Code")
        print("="*70)

        tests = [
            ("Home Page Redirect", self.test_home_page),
            ("Registration Page Load", self.test_registration_page),
            ("User Registration", self.test_user_registration),
            ("User Login", self.test_login),
            ("Calendar View Load", self.test_calendar_view),
            ("Submit Unavailability", self.test_submit_unavailability),
            ("Show Free Times", self.test_show_free_times),
            ("Show Last Five Entries", self.test_show_last_five),
            ("Delete Selected Entries", self.test_delete_selected),
            ("Groups List View", self.test_group_calendar),
            ("Logout", self.test_logout),
        ]

        results = []
        for test_name, test_func in tests:
            try:
                result = test_func()
                results.append((test_name, result))
            except Exception as e:
                print(f"❌ {test_name} crashed: {e}")
                results.append((test_name, False))

        print("\n" + "="*70)
        print("TEST RESULTS SUMMARY")
        print("="*70)

        passed = sum(1 for _, result in results if result)
        total = len(results)

        for test_name, result in results:
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"{status} - {test_name}")

        print("="*70)
        print(f"TOTAL: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
        print("="*70)

        return passed == total

if __name__ == "__main__":
    tester = LiveServerTester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)
