#!/usr/bin/env python
"""
Comprehensive Test Runner
Runs all tests (pylint, unit, fuzz, mutation, coverage) in the correct order
Stops on first failure and reports results
"""

import os
import sys
import subprocess
from typing import Tuple


class TestRunner:
    """Automated test runner for the meeting scheduler project"""

    def __init__(self):
        self.results = {
            'pylint': None,
            'unit_tests': None,
            'fuzz_tests': None,
            'all_tests': None,
            'mutation_tests': None,
            'coverage': None
        }
        self.failed_step = None

    def print_header(self, text: str):
        """Print a formatted header"""
        print("\n" + "="*70)
        print(f"  {text}")
        print("="*70 + "\n")

    def print_step(self, step_num: int, text: str):
        """Print step header"""
        print(f"\n{'='*70}")
        print(f"STEP {step_num}: {text}")
        print(f"{'='*70}\n")

    def run_command(self, cmd: list, description: str) -> Tuple[bool, str]:
        """Run a command and return success status and output"""
        try:
            print(f"Running: {' '.join(cmd)}\n")
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300
            )

            # Print output
            if result.stdout:
                print(result.stdout)
            if result.stderr:
                print(result.stderr)

            success = result.returncode == 0

            if success:
                print(f"\n[SUCCESS] {description}")
            else:
                print(f"\n[FAILED] {description}")
                print(f"Exit code: {result.returncode}")

            return success, result.stdout + result.stderr

        except subprocess.TimeoutExpired:
            print(f"\n[TIMEOUT] {description} took too long")
            return False, "Timeout expired"
        except Exception as e:
            print(f"\n[ERROR] {description} - {str(e)}")
            return False, str(e)

    def run_pylint(self) -> bool:
        """Step 1: Run pylint"""
        self.print_step(1, "PYLINT - Code Quality Check")

        cmd = [
            sys.executable, '-m', 'pylint',
            'calendar_app/models.py',
            'calendar_app/forms.py',
            'calendar_app/views.py',
            'calendar_app/urls.py',
            '--disable=C0114,C0115,C0116,R0903,R0914,R0912,R0915,E1101',
            '--max-line-length=120'
        ]

        success, output = self.run_command(cmd, "Pylint code quality check")
        self.results['pylint'] = success

        if not success:
            self.failed_step = "Pylint"
            print("\n" + "!"*70)
            print("ACTION REQUIRED: Fix all pylint findings before proceeding")
            print("!"*70)

        return success

    def run_unit_tests(self) -> bool:
        """Step 2: Run unit tests"""
        self.print_step(2, "UNIT TESTS")

        cmd = [
            sys.executable, 'manage.py', 'test',
            'calendar_app.tests',
            '--verbosity=2'
        ]

        success, output = self.run_command(cmd, "Unit tests (21 tests)")
        self.results['unit_tests'] = success

        if not success:
            self.failed_step = "Unit Tests"
            print("\n" + "!"*70)
            print("ACTION REQUIRED: Fix failing unit tests before proceeding")
            print("!"*70)

        return success

    def run_fuzz_tests(self) -> bool:
        """Step 3: Run fuzz tests"""
        self.print_step(3, "FUZZ TESTS")

        cmd = [
            sys.executable, 'manage.py', 'test',
            'calendar_app.test_fuzz',
            '--verbosity=2'
        ]

        success, output = self.run_command(cmd, "Fuzz tests (9 tests)")
        self.results['fuzz_tests'] = success

        if not success:
            self.failed_step = "Fuzz Tests"
            print("\n" + "!"*70)
            print("ACTION REQUIRED: Fix failing fuzz tests before proceeding")
            print("!"*70)

        return success

    def run_all_tests(self) -> bool:
        """Step 4: Run all tests together"""
        self.print_step(4, "ALL TESTS COMBINED")

        cmd = [
            sys.executable, 'manage.py', 'test',
            'calendar_app',
            '--verbosity=1'
        ]

        success, output = self.run_command(cmd, "All tests (30 tests)")
        self.results['all_tests'] = success

        if not success:
            self.failed_step = "All Tests"

        return success

    def run_mutation_tests(self) -> bool:
        """Step 5: Run mutation tests"""
        self.print_step(5, "MUTATION TESTS")

        cmd = [sys.executable, 'run_mutation_test.py']

        success, output = self.run_command(cmd, "Mutation tests")

        # Check if mutation score is 100%
        if "Mutation Score: 100.0%" in output:
            success = True
        else:
            success = False

        self.results['mutation_tests'] = success

        if not success:
            self.failed_step = "Mutation Tests"
            print("\n" + "!"*70)
            print("ACTION REQUIRED: Add tests to kill surviving mutations")
            print("!"*70)

        return success

    def run_coverage(self) -> bool:
        """Step 6: Generate coverage report"""
        self.print_step(6, "CODE COVERAGE")

        # Run coverage
        cmd1 = [
            sys.executable, '-m', 'coverage', 'run',
            '--source=calendar_app',
            'manage.py', 'test', 'calendar_app.tests'
        ]

        success1, _ = self.run_command(cmd1, "Collecting coverage data")

        if not success1:
            return False

        # Generate report
        cmd2 = [sys.executable, '-m', 'coverage', 'report']

        success2, output = self.run_command(cmd2, "Generating coverage report")

        # Check coverage thresholds
        success = success2
        if "views.py" in output:
            # Look for views.py coverage line
            for line in output.split('\n'):
                if 'views.py' in line:
                    try:
                        # Extract coverage percentage
                        parts = line.split()
                        coverage_pct = int(parts[-1].replace('%', ''))
                        if coverage_pct < 93:
                            print(f"\nWARNING: views.py coverage ({coverage_pct}%) below 93%")
                            success = False
                    except:
                        pass

        self.results['coverage'] = success

        if not success:
            self.failed_step = "Coverage"

        return success

    def print_summary(self):
        """Print final summary"""
        self.print_header("TEST SUMMARY")

        print("Test Results:")
        print(f"  1. Pylint:        {'PASS' if self.results['pylint'] else 'FAIL'}")
        print(f"  2. Unit Tests:    {'PASS' if self.results['unit_tests'] else 'FAIL'}")
        print(f"  3. Fuzz Tests:    {'PASS' if self.results['fuzz_tests'] else 'FAIL'}")
        print(f"  4. All Tests:     {'PASS' if self.results['all_tests'] else 'FAIL'}")
        print(f"  5. Mutation:      {'PASS' if self.results['mutation_tests'] else 'FAIL'}")
        print(f"  6. Coverage:      {'PASS' if self.results['coverage'] else 'FAIL'}")

        all_passed = all(v for v in self.results.values() if v is not None)

        print("\n" + "="*70)
        if all_passed:
            print("  [SUCCESS] ALL TESTS PASSED!")
            print("  Code is ready for deployment")
        else:
            print(f"  [FAILED] Tests failed at: {self.failed_step}")
            print("  Fix the errors and re-run this script")
        print("="*70 + "\n")

        return all_passed

    def run_all(self) -> bool:
        """Run all tests in sequence"""
        self.print_header("COMPREHENSIVE TEST RUNNER")
        print("Running all tests in sequence...")
        print("Will stop at first failure\n")

        # Step 1: Pylint
        if not self.run_pylint():
            self.print_summary()
            return False

        # Step 2: Unit tests
        if not self.run_unit_tests():
            self.print_summary()
            return False

        # Step 3: Fuzz tests
        if not self.run_fuzz_tests():
            self.print_summary()
            return False

        # Step 4: All tests
        if not self.run_all_tests():
            self.print_summary()
            return False

        # Step 5: Mutation tests
        if not self.run_mutation_tests():
            self.print_summary()
            return False

        # Step 6: Coverage
        if not self.run_coverage():
            self.print_summary()
            return False

        # Print summary
        return self.print_summary()


if __name__ == '__main__':
    os.chdir(os.path.dirname(os.path.abspath(__file__)))

    runner = TestRunner()
    success = runner.run_all()

    # Exit with appropriate code
    sys.exit(0 if success else 1)
