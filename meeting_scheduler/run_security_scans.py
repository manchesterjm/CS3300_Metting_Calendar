#!/usr/bin/env python
"""
Security Scan Runner

Runs all security scanning tools (Bandit, Safety, pip-audit, Semgrep) and
reports findings. This script should be run before committing code and can
be integrated into CI/CD pipelines.
"""

import sys
import subprocess
from typing import Tuple


class SecurityScanner:
    """Automated security scanner for the meeting scheduler project"""

    def __init__(self):
        self.results = {
            'bandit': None,
            'safety': None,
            'pip_audit': None,
            'semgrep': None
        }
        self.failed_scans = []

    def print_header(self, text: str):
        """Print a formatted header"""
        print("\n" + "="*70)
        print(f"  {text}")
        print("="*70 + "\n")

    def print_step(self, step_num: int, text: str):
        """Print step header"""
        print(f"\n{'='*70}")
        print(f"SECURITY SCAN {step_num}: {text}")
        print(f"{'='*70}\n")

    def run_command(self, cmd: list, description: str) -> Tuple[bool, str]:
        """
        Run a security scan command and return success status and output.

        Args:
            cmd: Command and arguments as list.
            description: Description of the scan being run.

        Returns:
            Tuple of (success: bool, output: str)
        """
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
                print(f"\n[WARNING] {description} - Found issues to review")

            return success, result.stdout + result.stderr

        except subprocess.TimeoutExpired:
            print(f"\n[TIMEOUT] {description} took too long")
            return False, "Timeout expired"
        except Exception as e:
            print(f"\n[ERROR] {description} - {str(e)}")
            return False, str(e)

    def run_bandit(self) -> bool:
        """Run Bandit static security analyzer"""
        self.print_step(1, "BANDIT - Python Security Linter")

        cmd = [
            sys.executable, '-m', 'bandit',
            '-r', 'calendar_app/',
            '--configfile', '.bandit',
            '-f', 'txt'
        ]

        success, output = self.run_command(cmd, "Bandit security scan")
        self.results['bandit'] = success

        if not success:
            self.failed_scans.append("Bandit")

        return success

    def run_safety(self) -> bool:
        """Run Safety dependency vulnerability scanner"""
        self.print_step(2, "SAFETY - Dependency Vulnerability Scanner")

        cmd = [
            sys.executable, '-m', 'safety',
            'scan'
        ]

        success, output = self.run_command(cmd, "Safety vulnerability scan")

        # Safety may return non-zero even for informational warnings
        # Check output for actual vulnerabilities
        if "vulnerabilities reported" in output.lower() or "vulnerabilities found" in output.lower():
            if "0 vulnerabilities" in output.lower():
                success = True
            else:
                success = False

        self.results['safety'] = success

        if not success:
            self.failed_scans.append("Safety")

        return success

    def run_pip_audit(self) -> bool:
        """Run pip-audit for dependency vulnerabilities"""
        self.print_step(3, "PIP-AUDIT - Dependency Vulnerability Checker")

        cmd = [
            sys.executable, '-m', 'pip_audit',
            '-r', 'requirements.txt'
        ]

        success, output = self.run_command(cmd, "pip-audit vulnerability check")
        self.results['pip_audit'] = success

        if not success:
            self.failed_scans.append("pip-audit")

        return success

    def run_semgrep(self) -> bool:
        """Run Semgrep for security pattern matching"""
        self.print_step(4, "SEMGREP - Security Pattern Scanner")

        cmd = [
            'semgrep',
            '--config=.semgrep.yml',
            'calendar_app/'
        ]

        success, output = self.run_command(cmd, "Semgrep security scan")
        self.results['semgrep'] = success

        if not success:
            self.failed_scans.append("Semgrep")

        return success

    def print_summary(self):
        """Print final summary of all security scans"""
        self.print_header("SECURITY SCAN SUMMARY")

        print("Scan Results:")
        print(f"  1. Bandit:      {'PASS' if self.results['bandit'] else 'ISSUES FOUND'}")
        print(f"  2. Safety:      {'PASS' if self.results['safety'] else 'ISSUES FOUND'}")
        print(f"  3. pip-audit:   {'PASS' if self.results['pip_audit'] else 'ISSUES FOUND'}")
        print(f"  4. Semgrep:     {'PASS' if self.results['semgrep'] else 'ISSUES FOUND'}")

        all_passed = all(v for v in self.results.values() if v is not None)

        print("\n" + "="*70)
        if all_passed:
            print("  [SUCCESS] ALL SECURITY SCANS PASSED!")
            print("  No security issues detected")
        else:
            print(f"  [WARNING] Security issues found in: {', '.join(self.failed_scans)}")
            print("  Review the output above and address findings")
        print("="*70 + "\n")

        return all_passed

    def run_all(self) -> bool:
        """Run all security scans"""
        self.print_header("SECURITY SCANNER")
        print("Running all security scans...")
        print("Note: Some scans may show warnings even if no critical issues exist\n")

        # Run all scans (don't stop on first failure, collect all results)
        self.run_bandit()
        self.run_safety()
        self.run_pip_audit()
        self.run_semgrep()

        # Print summary
        return self.print_summary()


if __name__ == '__main__':
    scanner = SecurityScanner()
    success = scanner.run_all()

    # Exit with appropriate code
    # Note: We exit 0 even if some scans found issues (warnings),
    # to allow this to be informational in CI/CD rather than blocking
    sys.exit(0)
