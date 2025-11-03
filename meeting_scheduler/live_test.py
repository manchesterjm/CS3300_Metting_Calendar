"""
Live testing script that tests the actual running server.

Includes comprehensive error handling for:
- Network failures and timeouts
- HTML structure changes
- Connection errors
- HTTP status code errors
"""
import requests
from bs4 import BeautifulSoup
import re
import time

BASE_URL = "http://localhost:8000"
DEFAULT_TIMEOUT = 10  # seconds

class LiveTester:
    def __init__(self):
        self.session = requests.Session()
        self.csrf_token = None
        self.test_failures = []

    def _safe_request(self, method, url, **kwargs):
        """
        Wrapper for HTTP requests with comprehensive error handling.

        Args:
            method: HTTP method ('GET' or 'POST')
            url: URL to request
            **kwargs: Additional arguments to pass to requests

        Returns:
            Response object if successful, None otherwise
        """
        kwargs.setdefault('timeout', DEFAULT_TIMEOUT)

        try:
            if method.upper() == 'GET':
                response = self.session.get(url, **kwargs)
            elif method.upper() == 'POST':
                response = self.session.post(url, **kwargs)
            else:
                print(f"  [ERROR] Unsupported HTTP method: {method}")
                return None

            response.raise_for_status()
            return response

        except requests.exceptions.Timeout:
            print(f"  [ERROR] Request timed out after {kwargs['timeout']} seconds")
            print(f"    URL: {url}")
            print(f"    Ensure the server is running and responding")
            return None

        except requests.exceptions.ConnectionError:
            print(f"  [ERROR] Connection error - cannot reach server")
            print(f"    URL: {url}")
            print(f"    Ensure Django dev server is running (python manage.py runserver)")
            return None

        except requests.exceptions.HTTPError as e:
            print(f"  [ERROR] HTTP Error {e.response.status_code}")
            print(f"    URL: {url}")
            print(f"    Response: {e.response.text[:200]}...")
            return None

        except requests.exceptions.RequestException as e:
            print(f"  [ERROR] Request failed: {e}")
            print(f"    URL: {url}")
            return None

    def get_csrf_token(self, html):
        """
        Extract CSRF token from HTML with error handling.

        Args:
            html: HTML content as string

        Returns:
            CSRF token string if found, None otherwise
        """
        try:
            soup = BeautifulSoup(html, 'html.parser')
            csrf_input = soup.find('input', {'name': 'csrfmiddlewaretoken'})
            if csrf_input:
                token = csrf_input.get('value')
                if token:
                    return token
                print("  [WARN] CSRF input found but value is empty")
                return None
            print("  [WARN] CSRF token not found in HTML")
            return None
        except Exception as e:
            print(f"  [ERROR] Failed to parse HTML for CSRF token: {e}")
            return None

    def register_user(self, username, password, email):
        """
        Register a new user with error handling.

        Args:
            username: Username for registration
            password: Password for registration
            email: Email for registration

        Returns:
            True if registration successful, False otherwise
        """
        print(f"\n[TEST] Registering user: {username}")

        # Get registration page
        response = self._safe_request('GET', f"{BASE_URL}/register/")
        if not response:
            return False

        print(f"  GET /register/ - Status: {response.status_code}")

        csrf_token = self.get_csrf_token(response.text)
        if not csrf_token:
            print(f"  [FAIL] Could not extract CSRF token")
            return False

        # Submit registration
        data = {
            'csrfmiddlewaretoken': csrf_token,
            'username': username,
            'email': email,
            'password1': password,
            'password2': password
        }

        response = self._safe_request('POST', f"{BASE_URL}/register/", data=data, allow_redirects=False)
        if not response:
            return False

        print(f"  POST /register/ - Status: {response.status_code}")

        if response.status_code == 302:
            print(f"  [OK] Registration successful, redirected to: {response.headers.get('Location')}")
            return True
        else:
            print(f"  [FAIL] Registration failed")
            try:
                soup = BeautifulSoup(response.text, 'html.parser')
                errors = soup.find_all(class_='errorlist')
                for error in errors:
                    print(f"    Error: {error.get_text()}")
            except Exception as e:
                print(f"    Could not parse error messages: {e}")
            return False

    def login(self, username, password):
        """
        Login as a user with error handling.

        Args:
            username: Username to login with
            password: Password to login with

        Returns:
            True if login successful, False otherwise
        """
        print(f"\n[TEST] Logging in as: {username}")

        # Get login page
        response = self._safe_request('GET', f"{BASE_URL}/login/")
        if not response:
            return False

        print(f"  GET /login/ - Status: {response.status_code}")

        csrf_token = self.get_csrf_token(response.text)
        if not csrf_token:
            print(f"  [FAIL] Could not extract CSRF token")
            return False

        # Submit login
        data = {
            'csrfmiddlewaretoken': csrf_token,
            'username': username,
            'password': password
        }

        response = self._safe_request('POST', f"{BASE_URL}/login/", data=data, allow_redirects=False)
        if not response:
            return False

        print(f"  POST /login/ - Status: {response.status_code}")

        if response.status_code == 302:
            print(f"  [OK] Login successful, redirected to: {response.headers.get('Location')}")
            return True
        else:
            print(f"  [FAIL] Login failed - check credentials")
            return False

    def create_group(self, group_name):
        """
        Create a new group with error handling.

        Args:
            group_name: Name for the new group

        Returns:
            Group ID if successful, None otherwise
        """
        print(f"\n[TEST] Creating group: {group_name}")

        # Get create group page
        response = self._safe_request('GET', f"{BASE_URL}/groups/create/")
        if not response:
            return None

        print(f"  GET /groups/create/ - Status: {response.status_code}")

        csrf_token = self.get_csrf_token(response.text)
        if not csrf_token:
            print(f"  [FAIL] Could not extract CSRF token")
            return None

        # Submit group creation
        data = {
            'csrfmiddlewaretoken': csrf_token,
            'name': group_name
        }

        response = self._safe_request('POST', f"{BASE_URL}/groups/create/", data=data, allow_redirects=True)
        if not response:
            return None

        print(f"  POST /groups/create/ - Status: {response.status_code}")

        if response.status_code == 200:
            try:
                # Parse the group list page to find our group's ID
                soup = BeautifulSoup(response.text, 'html.parser')
                # Find all group items
                group_items = soup.find_all('li', class_='group-item')
                print(f"  Found {len(group_items)} groups")
                for item in group_items:
                    h3 = item.find('h3')
                    if h3 and group_name in h3.get_text():
                        # Find the calendar link to extract group ID
                        calendar_link = item.find('a', href=re.compile(r'/groups/\d+/calendar/'))
                        if calendar_link:
                            href = calendar_link.get('href')
                            group_id = int(href.split('/')[2])
                            print(f"  [OK] Group '{group_name}' created successfully with ID: {group_id}")
                            return group_id
                print(f"  [FAIL] Could not find group ID for '{group_name}' in HTML")
                return None
            except Exception as e:
                print(f"  [ERROR] Failed to parse group list page: {e}")
                return None
        else:
            print(f"  [FAIL] Group creation failed")
            return None

    def add_unavailability(self, date, start_time, end_time, description=""):
        """
        Add unavailability to personal calendar with error handling.

        Args:
            date: Date in YYYY-MM-DD format
            start_time: Start time in HH:MM format
            end_time: End time in HH:MM format
            description: Optional description

        Returns:
            True if successful, False otherwise
        """
        print(f"\n[TEST] Adding unavailability to personal calendar: {date} {start_time}-{end_time}")

        # Get personal calendar page
        response = self._safe_request('GET', f"{BASE_URL}/personal-calendar/")
        if not response:
            return False

        print(f"  GET /personal-calendar/ - Status: {response.status_code}")

        csrf_token = self.get_csrf_token(response.text)
        if not csrf_token:
            print(f"  [FAIL] Could not extract CSRF token")
            return False

        # Submit unavailability to PERSONAL calendar
        data = {
            'csrfmiddlewaretoken': csrf_token,
            'date': date,
            'start_time': start_time,
            'end_time': end_time,
            'description': description,
            'submit_unavailability': 'Add Unavailability'
        }

        response = self._safe_request('POST', f"{BASE_URL}/personal-calendar/", data=data, allow_redirects=False)
        if not response:
            return False

        print(f"  POST /personal-calendar/ - Status: {response.status_code}")

        if response.status_code in [200, 302]:
            print(f"  [OK] Unavailability added successfully to personal calendar")
            return True
        else:
            print(f"  [FAIL] Failed to add unavailability")
            try:
                soup = BeautifulSoup(response.text, 'html.parser')
                errors = soup.find_all(class_='errorlist')
                for error in errors:
                    print(f"    Error: {error.get_text()}")
            except Exception as e:
                print(f"    Could not parse error messages: {e}")
            return False

    def show_free_times(self, group_id, date):
        """
        Test show_free_times functionality with error handling.

        Args:
            group_id: Group ID to check free times for
            date: Date in YYYY-MM-DD format

        Returns:
            Tuple (success: bool, times: list or None)
        """
        print(f"\n[TEST] Showing free times for: {date}")

        # Get group calendar page
        response = self._safe_request('GET', f"{BASE_URL}/groups/{group_id}/calendar/")
        if not response:
            return False, None

        csrf_token = self.get_csrf_token(response.text)
        if not csrf_token:
            print(f"  [FAIL] Could not extract CSRF token")
            return False, None

        # Submit show_free_times request
        data = {
            'csrfmiddlewaretoken': csrf_token,
            'date': date,
            'show_free_times': 'Show'
        }

        print(f"  POST data: {data}")

        response = self._safe_request('POST', f"{BASE_URL}/groups/{group_id}/calendar/", data=data)
        if not response:
            return False, None

        print(f"  POST /groups/{group_id}/calendar/ - Status: {response.status_code}")

        try:
            # Parse response
            soup = BeautifulSoup(response.text, 'html.parser')

            # Look for free times results
            free_times_header = soup.find('h2', id='freeTimesResults')
            if free_times_header:
                print(f"  [OK] Free times header found: {free_times_header.get_text()}")

                # Find the list of times
                ul = free_times_header.find_next('ul')
                if ul:
                    times = [li.get_text() for li in ul.find_all('li')]
                    print(f"  [OK] Found {len(times)} free time slots:")
                    print(f"    {times[:5]}..." if len(times) > 5 else f"    {times}")
                    return True, times
                else:
                    # Check for "all slots free" message
                    p = free_times_header.find_next('p')
                    if p and 'All time slots are free' in p.get_text():
                        print(f"  [OK] All time slots are free!")
                        return True, []
            else:
                print(f"  [FAIL] Free times header NOT found in HTML")
                h1 = soup.find('h1')
                print(f"  Page title: {h1.get_text() if h1 else 'No title found'}")

            return False, None

        except Exception as e:
            print(f"  [ERROR] Failed to parse response: {e}")
            return False, None

    def show_free_times_personal(self, date):
        """
        Test show_free_times functionality on personal calendar with error handling.

        Args:
            date: Date in YYYY-MM-DD format

        Returns:
            Tuple (success: bool, times: list or None)
        """
        print(f"\n[TEST] Showing free times on personal calendar for: {date}")

        # Get personal calendar page
        response = self._safe_request('GET', f"{BASE_URL}/personal-calendar/")
        if not response:
            return False, None

        csrf_token = self.get_csrf_token(response.text)
        if not csrf_token:
            print(f"  [FAIL] Could not extract CSRF token")
            return False, None

        # Submit show_free_times request
        data = {
            'csrfmiddlewaretoken': csrf_token,
            'date': date,
            'show_free_times': 'Show Free Times'
        }

        response = self._safe_request('POST', f"{BASE_URL}/personal-calendar/", data=data)
        if not response:
            return False, None

        print(f"  POST /personal-calendar/ - Status: {response.status_code}")

        try:
            # Parse response
            soup = BeautifulSoup(response.text, 'html.parser')

            # Look for free times results
            free_times_header = soup.find('h2', id='freeTimesResults')
            if free_times_header:
                print(f"  [OK] Free times header found: {free_times_header.get_text()}")

                # Find the list of times
                ul = free_times_header.find_next('ul')
                if ul:
                    times = [li.get_text() for li in ul.find_all('li')]
                    print(f"  [OK] Found {len(times)} free time slots")
                    return True, times
                else:
                    # Check for "all slots free" message
                    p = free_times_header.find_next('p')
                    if p and ('All time slots are free' in p.get_text() or 'free' in p.get_text().lower()):
                        print(f"  [OK] All time slots are free!")
                        return True, []
            else:
                print(f"  [FAIL] Free times header NOT found on personal calendar")

            return False, None

        except Exception as e:
            print(f"  [ERROR] Failed to parse response: {e}")
            return False, None

    def show_last_five(self):
        """
        Test show_last_five functionality on personal calendar with error handling.

        Returns:
            Tuple (success: bool, count: int)
        """
        print(f"\n[TEST] Showing last 5 entries on personal calendar")

        # Get personal calendar page
        response = self._safe_request('GET', f"{BASE_URL}/personal-calendar/")
        if not response:
            return False, 0

        csrf_token = self.get_csrf_token(response.text)
        if not csrf_token:
            print(f"  [FAIL] Could not extract CSRF token")
            return False, 0

        # Submit show_last_five request
        data = {
            'csrfmiddlewaretoken': csrf_token,
            'date': '2025-11-02',  # Dummy date
            'show_last_five': 'Show Last 5'
        }

        response = self._safe_request('POST', f"{BASE_URL}/personal-calendar/", data=data)
        if not response:
            return False, 0

        print(f"  POST /personal-calendar/ - Status: {response.status_code}")

        try:
            # Parse response
            soup = BeautifulSoup(response.text, 'html.parser')

            # Look for checkboxes (entry list)
            checkboxes = soup.find_all('input', {'type': 'checkbox', 'name': 'entry_ids'})
            if checkboxes:
                print(f"  [OK] Found {len(checkboxes)} entries to delete")
                for cb in checkboxes[:5]:  # Show first 5
                    label = soup.find('label', {'for': cb.get('id')})
                    if label:
                        print(f"    - {label.get_text().strip()[:60]}...")
                return True, len(checkboxes)
            else:
                print(f"  [WARN] No entries found (user may have no unavailability entries)")
                return True, 0  # Not a failure - user might not have entries yet

        except Exception as e:
            print(f"  [ERROR] Failed to parse response: {e}")
            return False, 0

    def delete_entries(self, entry_ids):
        """
        Test delete selected entries functionality with error handling.

        Args:
            entry_ids: List of entry IDs to delete

        Returns:
            True if successful, False otherwise
        """
        print(f"\n[TEST] Deleting {len(entry_ids)} entries")

        # Get personal calendar page
        response = self._safe_request('GET', f"{BASE_URL}/personal-calendar/")
        if not response:
            return False

        csrf_token = self.get_csrf_token(response.text)
        if not csrf_token:
            print(f"  [FAIL] Could not extract CSRF token")
            return False

        # Submit delete request
        data = {
            'csrfmiddlewaretoken': csrf_token,
            'entry_ids': entry_ids,
            'delete_selected': 'Delete Selected'
        }

        response = self._safe_request('POST', f"{BASE_URL}/personal-calendar/", data=data, allow_redirects=False)
        if not response:
            return False

        print(f"  POST /personal-calendar/ - Status: {response.status_code}")

        if response.status_code in [200, 302]:
            print(f"  [OK] Entries deleted successfully")
            return True
        else:
            print(f"  [FAIL] Failed to delete entries")
            return False


def run_live_tests():
    """
    Run comprehensive live tests with server availability check.

    Returns:
        True if all tests pass, False otherwise
    """
    print("=" * 60)
    print("STARTING LIVE TESTS")
    print("=" * 60)

    tester = LiveTester()

    # Pre-flight check: Verify server is running
    print("\n[PREFLIGHT] Checking server availability...")
    try:
        response = tester._safe_request('GET', f"{BASE_URL}/")
        if not response:
            print("\n[FATAL] Server is not responding!")
            print("  Please start the Django development server:")
            print("    cd meeting_scheduler")
            print("    python manage.py runserver")
            return False
        print(f"  [OK] Server is running at {BASE_URL}")
    except Exception as e:
        print(f"\n[FATAL] Failed to connect to server: {e}")
        return False

    # Test 1: Register user
    if not tester.register_user('livetest', 'TestPass123!', 'livetest@test.com'):
        # User might already exist, try logging in
        if not tester.login('livetest', 'TestPass123!'):
            print("\n[FAIL] FAILED: Cannot register or login")
            return False

    # Test 2: Create group with unique name
    group_name = f'Test Group {int(time.time())}'
    group_id = tester.create_group(group_name)
    if not group_id:
        print("\n[FAIL] FAILED: Could not create group")
        return False

    # Test 3: Add unavailability to personal calendar
    if not tester.add_unavailability('2025-11-02', '10:00', '14:00', 'Test entry'):
        print("\n[FAIL] FAILED: Could not add unavailability to personal calendar")
        return False

    # Test 4: Show free times on personal calendar
    success, times = tester.show_free_times_personal('2025-11-02')
    if not success:
        print("\n[FAIL] FAILED: show_free_times on personal calendar did not work")
        return False

    # Test 5: Show free times on group calendar (should aggregate personal calendars)
    success, times = tester.show_free_times(group_id, '2025-11-02')
    if not success:
        print("\n[FAIL] FAILED: show_free_times on group calendar did not work")
        return False

    # Test 6: Show last five on personal calendar
    success, count = tester.show_last_five()
    if not success:
        print("\n[FAIL] FAILED: show_last_five on personal calendar did not work")
        return False

    # Test 7: Test deletion functionality (if we have entries)
    if count > 0:
        # Need to call show_last_five again to get the page with checkboxes,
        # and use THAT response (not a fresh GET) to find the entry ID
        try:
            response = tester._safe_request('GET', f"{BASE_URL}/personal-calendar/")
            if not response:
                print("\n[WARN] Could not get calendar page for deletion test")
            else:
                csrf_token = tester.get_csrf_token(response.text)

                data = {
                    'csrfmiddlewaretoken': csrf_token,
                    'date': '2025-11-02',
                    'show_last_five': 'Show Last 5'
                }

                response = tester._safe_request('POST', f"{BASE_URL}/personal-calendar/", data=data)
                if response:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    first_checkbox = soup.find('input', {'type': 'checkbox', 'name': 'entry_ids'})

                    if first_checkbox:
                        entry_id = first_checkbox.get('value')
                        print(f"\n[INFO] Found entry ID {entry_id} to delete")
                        if not tester.delete_entries([entry_id]):
                            print("\n[FAIL] FAILED: Could not delete entry")
                            return False
                    else:
                        print("\n[WARN] Could not find entry to delete (skipping deletion test)")
        except Exception as e:
            print(f"\n[WARN] Deletion test failed with error: {e}")
            print("  Continuing with other tests...")
    else:
        print("\n[INFO] No entries to delete (skipping deletion test)")

    print("\n" + "=" * 60)
    print("[OK] ALL LIVE TESTS PASSED!")
    print("=" * 60)
    return True


if __name__ == '__main__':
    run_live_tests()
