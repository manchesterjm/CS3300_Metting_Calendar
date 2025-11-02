"""
Live testing script that tests the actual running server.
"""
import requests
from bs4 import BeautifulSoup
import re

BASE_URL = "http://localhost:8000"

class LiveTester:
    def __init__(self):
        self.session = requests.Session()
        self.csrf_token = None

    def get_csrf_token(self, html):
        """Extract CSRF token from HTML"""
        soup = BeautifulSoup(html, 'html.parser')
        csrf_input = soup.find('input', {'name': 'csrfmiddlewaretoken'})
        if csrf_input:
            return csrf_input.get('value')
        return None

    def register_user(self, username, password, email):
        """Register a new user"""
        print(f"\n[TEST] Registering user: {username}")

        # Get registration page
        response = self.session.get(f"{BASE_URL}/register/")
        print(f"  GET /register/ - Status: {response.status_code}")

        csrf_token = self.get_csrf_token(response.text)

        # Submit registration
        data = {
            'csrfmiddlewaretoken': csrf_token,
            'username': username,
            'email': email,
            'password1': password,
            'password2': password
        }

        response = self.session.post(f"{BASE_URL}/register/", data=data, allow_redirects=False)
        print(f"  POST /register/ - Status: {response.status_code}")

        if response.status_code == 302:
            print(f"  [OK] Registration successful, redirected to: {response.headers.get('Location')}")
            return True
        else:
            print(f"  [FAIL] Registration failed")
            soup = BeautifulSoup(response.text, 'html.parser')
            errors = soup.find_all(class_='errorlist')
            for error in errors:
                print(f"    Error: {error.get_text()}")
            return False

    def login(self, username, password):
        """Login as a user"""
        print(f"\n[TEST] Logging in as: {username}")

        # Get login page
        response = self.session.get(f"{BASE_URL}/login/")
        print(f"  GET /login/ - Status: {response.status_code}")

        csrf_token = self.get_csrf_token(response.text)

        # Submit login
        data = {
            'csrfmiddlewaretoken': csrf_token,
            'username': username,
            'password': password
        }

        response = self.session.post(f"{BASE_URL}/login/", data=data, allow_redirects=False)
        print(f"  POST /login/ - Status: {response.status_code}")

        if response.status_code == 302:
            print(f"  [OK] Login successful, redirected to: {response.headers.get('Location')}")
            return True
        else:
            print(f"  [FAIL] Login failed")
            return False

    def create_group(self, group_name):
        """Create a new group"""
        print(f"\n[TEST] Creating group: {group_name}")

        # Get create group page
        response = self.session.get(f"{BASE_URL}/groups/create/")
        print(f"  GET /groups/create/ - Status: {response.status_code}")

        csrf_token = self.get_csrf_token(response.text)

        # Submit group creation
        data = {
            'csrfmiddlewaretoken': csrf_token,
            'name': group_name
        }

        response = self.session.post(f"{BASE_URL}/groups/create/", data=data, allow_redirects=True)
        print(f"  POST /groups/create/ - Status: {response.status_code}")

        if response.status_code == 200:
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
            print(f"  [FAIL] Could not find group ID for '{group_name}'")
            return None
        else:
            print(f"  [FAIL] Group creation failed")
            return None

    def add_unavailability(self, group_id, date, start_time, end_time, description=""):
        """Add unavailability to group calendar"""
        print(f"\n[TEST] Adding unavailability: {date} {start_time}-{end_time}")

        # Get group calendar page
        response = self.session.get(f"{BASE_URL}/groups/{group_id}/calendar/")
        print(f"  GET /groups/{group_id}/calendar/ - Status: {response.status_code}")

        csrf_token = self.get_csrf_token(response.text)

        # Submit unavailability
        data = {
            'csrfmiddlewaretoken': csrf_token,
            'date': date,
            'start_time': start_time,
            'end_time': end_time,
            'description': description,
            'submit_unavailability': 'Submit'
        }

        response = self.session.post(
            f"{BASE_URL}/groups/{group_id}/calendar/",
            data=data,
            allow_redirects=False
        )
        print(f"  POST /groups/{group_id}/calendar/ - Status: {response.status_code}")

        if response.status_code == 302:
            print(f"  [OK] Unavailability added successfully")
            return True
        else:
            print(f"  [FAIL] Failed to add unavailability")
            soup = BeautifulSoup(response.text, 'html.parser')
            errors = soup.find_all(class_='errorlist')
            for error in errors:
                print(f"    Error: {error.get_text()}")
            return False

    def show_free_times(self, group_id, date):
        """Test show_free_times functionality"""
        print(f"\n[TEST] Showing free times for: {date}")

        # Get group calendar page
        response = self.session.get(f"{BASE_URL}/groups/{group_id}/calendar/")
        csrf_token = self.get_csrf_token(response.text)

        # Submit show_free_times request
        data = {
            'csrfmiddlewaretoken': csrf_token,
            'date': date,
            'show_free_times': 'Show'
        }

        print(f"  POST data: {data}")

        response = self.session.post(
            f"{BASE_URL}/groups/{group_id}/calendar/",
            data=data
        )
        print(f"  POST /groups/{group_id}/calendar/ - Status: {response.status_code}")

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
            print(f"  [FAIL] Free times header NOT found")
            print(f"  Page title: {soup.find('h1').get_text() if soup.find('h1') else 'No title'}")

        return False, None

    def show_last_five(self, group_id):
        """Test show_last_five functionality"""
        print(f"\n[TEST] Showing last 5 entries")

        # Get group calendar page
        response = self.session.get(f"{BASE_URL}/groups/{group_id}/calendar/")
        csrf_token = self.get_csrf_token(response.text)

        # Submit show_last_five request
        data = {
            'csrfmiddlewaretoken': csrf_token,
            'date': '2025-11-02',  # Dummy date
            'show_last_five': 'Show'
        }

        response = self.session.post(
            f"{BASE_URL}/groups/{group_id}/calendar/",
            data=data
        )
        print(f"  POST /groups/{group_id}/calendar/ - Status: {response.status_code}")

        # Parse response
        soup = BeautifulSoup(response.text, 'html.parser')

        # Look for checkboxes (entry list)
        checkboxes = soup.find_all('input', {'type': 'checkbox', 'name': 'entry_ids'})
        if checkboxes:
            print(f"  [OK] Found {len(checkboxes)} entries to delete")
            for cb in checkboxes:
                label = soup.find('label', {'for': cb.get('id')})
                if label:
                    print(f"    - {label.get_text()}")
            return True, len(checkboxes)
        else:
            print(f"  [FAIL] No entries found")
            return False, 0


def run_live_tests():
    """Run comprehensive live tests"""
    import time
    print("=" * 60)
    print("STARTING LIVE TESTS")
    print("=" * 60)

    tester = LiveTester()

    # Test 1: Register user
    if not tester.register_user('livetest', 'TestPass123!', 'livetest@test.com'):
        # User might already exist, try logging in
        if not tester.login('livetest', 'TestPass123!'):
            print("\n[FAIL] FAILED: Cannot register or login")
            return

    # Test 2: Create group with unique name
    group_name = f'Test Group {int(time.time())}'
    group_id = tester.create_group(group_name)
    if not group_id:
        print("\n[FAIL] FAILED: Could not create group")
        return

    # Test 3: Add unavailability
    if not tester.add_unavailability(group_id, '2025-11-02', '10:00', '14:00', 'Test entry'):
        print("\n[FAIL] FAILED: Could not add unavailability")
        return

    # Test 4: Show free times (should work now!)
    success, times = tester.show_free_times(group_id, '2025-11-02')
    if not success:
        print("\n[FAIL] FAILED: show_free_times did not work")
        return

    # Test 5: Show last five
    success, count = tester.show_last_five(group_id)
    if not success:
        print("\n[FAIL] FAILED: show_last_five did not work")
        return

    print("\n" + "=" * 60)
    print("[OK] ALL LIVE TESTS PASSED!")
    print("=" * 60)


if __name__ == '__main__':
    run_live_tests()
