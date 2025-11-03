"""
Admin interface tests for calendar_app

Tests for:
- CustomUserAdmin registration and configuration
- Admin password generation functionality
- Admin permissions and access control

Addresses AI Code Review Issue #17: Custom Admin Missing Test Coverage
"""
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.contrib.admin.sites import site


class CustomUserAdminTest(TestCase):
    """Tests for CustomUserAdmin functionality"""

    def setUp(self):
        """Set up test data"""
        # Create superuser for admin access
        self.admin_user = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='adminpass123'
        )
        # Create regular user for testing
        self.test_user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client = Client()

    def test_custom_user_admin_registered(self):
        """Test that CustomUserAdmin is properly registered"""
        from django.contrib.auth.models import User as DjangoUser
        # Verify User model is registered with admin
        self.assertIn(DjangoUser, site._registry)
        # Get the admin class
        admin_class = site._registry[DjangoUser]
        # Verify it's our custom admin (not Django's default)
        self.assertEqual(admin_class.__class__.__name__, 'CustomUserAdmin')

    def test_admin_change_password_template_override(self):
        """Test that custom change password template is used"""
        from django.contrib.auth.models import User as DjangoUser
        admin_class = site._registry[DjangoUser]
        # Check that change_user_password_template is set
        self.assertEqual(
            admin_class.change_user_password_template,
            'admin/auth/user/change_password.html'
        )

    def test_admin_user_changelist_access(self):
        """Test that admin can access user changelist"""
        self.client.login(username='admin', password='adminpass123')
        response = self.client.get(reverse('admin:auth_user_changelist'))
        self.assertEqual(response.status_code, 200)
        # Should show both admin and test user
        self.assertContains(response, 'admin')
        self.assertContains(response, 'testuser')

    def test_admin_user_change_form_access(self):
        """Test that admin can access user change form"""
        self.client.login(username='admin', password='adminpass123')
        response = self.client.get(
            reverse('admin:auth_user_change', args=[self.test_user.id])
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'testuser')

    def test_admin_user_password_change_access(self):
        """Test that admin can access user password change form"""
        self.client.login(username='admin', password='adminpass123')
        response = self.client.get(
            reverse('admin:auth_user_password_change', args=[self.test_user.id])
        )
        self.assertEqual(response.status_code, 200)
        # Should show password change form
        self.assertContains(response, 'password')
        # Should show the username
        self.assertContains(response, 'testuser')

    def test_non_admin_cannot_access_user_admin(self):
        """Test that non-admin users cannot access user admin"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('admin:auth_user_changelist'))
        # Should redirect to login (not authorized)
        self.assertEqual(response.status_code, 302)
        self.assertIn('/admin/login/', response.url)

    def test_admin_can_change_user_password(self):
        """Test that admin can successfully change a user's password"""
        self.client.login(username='admin', password='adminpass123')
        post_data = {
            'password1': 'NewSecurePass123!',
            'password2': 'NewSecurePass123!'
        }
        response = self.client.post(
            reverse('admin:auth_user_password_change', args=[self.test_user.id]),
            post_data
        )
        # Should redirect after successful password change
        self.assertEqual(response.status_code, 302)

        # Verify password was actually changed
        self.test_user.refresh_from_db()
        self.assertTrue(self.test_user.check_password('NewSecurePass123!'))

    def test_admin_user_add_form(self):
        """Test that admin can add new users"""
        self.client.login(username='admin', password='adminpass123')
        response = self.client.get(reverse('admin:auth_user_add'))
        self.assertEqual(response.status_code, 200)
        # Should show user creation form
        self.assertContains(response, 'username')
        self.assertContains(response, 'password')

    def test_admin_preserves_django_default_behavior(self):
        """Test that our CustomUserAdmin doesn't break default Django admin behavior"""
        from django.contrib.auth.models import User as DjangoUser
        admin_class = site._registry[DjangoUser]

        # Should still have all standard admin methods
        self.assertTrue(hasattr(admin_class, 'get_urls'))
        self.assertTrue(hasattr(admin_class, 'user_change_password'))
        self.assertTrue(hasattr(admin_class, 'has_add_permission'))
        self.assertTrue(hasattr(admin_class, 'has_change_permission'))
        self.assertTrue(hasattr(admin_class, 'has_delete_permission'))
