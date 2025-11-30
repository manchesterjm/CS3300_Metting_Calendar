#!/bin/bash
# Wrapper script for mutmut to run tests from the correct directory
cd "$(dirname "$0")"
pytest calendar_app/tests/ -x --tb=no -q --no-cov
