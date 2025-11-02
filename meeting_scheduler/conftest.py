"""
Pytest configuration and fixtures for the Meeting Scheduler project.

This module provides shared pytest configuration and fixtures for all tests.
"""
import os
import sys
import django
from pathlib import Path

# Add the project directory to Python path
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

# Set up Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'meeting_scheduler.settings')

# Initialize Django
django.setup()


def pytest_configure(config):
    """
    Configure pytest before test run.

    Sets up Django test environment and configures coverage.
    """
    # Disable Django debug mode for tests
    from django.conf import settings
    settings.DEBUG = False

    # Configure coverage to exclude test files
    if config.option.cov_source:
        # Add exclusions to coverage
        config.option.cov_config = '.coveragerc'


def pytest_collection_modifyitems(config, items):
    """
    Modify test items after collection.

    Can be used to add markers or modify test behavior.
    """
    pass
