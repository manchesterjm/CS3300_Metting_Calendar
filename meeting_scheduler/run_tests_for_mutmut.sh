#!/bin/bash
# Wrapper script for mutmut to run tests from the correct directory
# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# Change to that directory (meeting_scheduler/)
cd "$SCRIPT_DIR"
python manage.py test calendar_app.tests --verbosity=0
