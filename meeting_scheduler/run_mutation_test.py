"""
Manual Mutation Testing Script

Demonstrates mutation testing by applying mutations to code and running tests.
Implements custom mutation framework for Django applications.

Mutation Types: Boundary conditions, return values, logic operators
Target Score: 100% (all mutations killed)
Last Updated: 2025-01-11
"""
import os
import subprocess
import sys
import shutil


class MutationTester:
    """Simple mutation testing framework"""

    def __init__(self):
        self.results = {
            'killed': [],
            'survived': [],
            'errors': []
        }

    def run_tests(self):
        """Run the test suite and return result"""
        try:
            result = subprocess.run(
                [sys.executable, 'manage.py', 'test', 'calendar_app.tests', '--verbosity=0'],
                capture_output=True,
                text=True,
                timeout=120
            )
            return result.returncode == 0
        except subprocess.TimeoutExpired:
            print("  [TIMEOUT] Tests timed out after 120 seconds")
            return False  # Timeout means mutation likely caused infinite loop = killed
        except Exception as e:
            print(f"  [ERROR] Error running tests: {e}")
            return None

    def apply_mutation(self, filepath, original, mutated, description):
        """Apply a mutation to a file"""
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        if original not in content:
            print(f"[WARNING] Original code not found for: {description}")
            return False

        mutated_content = content.replace(original, mutated, 1)

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(mutated_content)

        return True

    def revert_mutation(self, filepath, original, mutated):
        """Revert a mutation"""
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        reverted_content = content.replace(mutated, original, 1)

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(reverted_content)

    def test_mutation(self, filepath, original, mutated, description):
        """Test a single mutation"""
        print(f"\nTesting: {description}")
        print(f"  File: {filepath}")
        print(f"  Original: {original[:50]}...")
        print(f"  Mutated:  {mutated[:50]}...")

        # Backup original file
        backup_path = filepath + '.backup'
        shutil.copy(filepath, backup_path)

        try:
            # Apply mutation
            if not self.apply_mutation(filepath, original, mutated, description):
                self.results['errors'].append(description)
                return

            # Run tests
            tests_pass = self.run_tests()

            if tests_pass is None:
                print("  [ERROR] Test execution failed")
                self.results['errors'].append(description)
            elif tests_pass:
                print("  [SURVIVED] Tests still pass with mutation!")
                self.results['survived'].append(description)
            else:
                print("  [KILLED] Tests caught the mutation")
                self.results['killed'].append(description)

        finally:
            # Restore original file
            shutil.move(backup_path, filepath)

    def run_all_mutations(self):
        """Run all defined mutations"""
        print("="*70)
        print("MUTATION TESTING - Updated for SOFA Refactoring")
        print("="*70)

        # Mutation 1: Change time increment in free time calculation (NOW IN SERVICES)
        self.test_mutation(
            'calendar_app/services.py',
            'current += datetime.timedelta(minutes=interval_minutes)',
            'current += datetime.timedelta(minutes=interval_minutes * 2)',
            'Mutation 1: Change time slot increment'
        )

        # Mutation 2: Change start time constant (NOW IN SERVICES)
        self.test_mutation(
            'calendar_app/services.py',
            'DEFAULT_START_HOUR = 8',
            'DEFAULT_START_HOUR = 9',
            'Mutation 2: Change default start hour from 8 to 9'
        )

        # Mutation 3: Change end time constant (NOW IN SERVICES)
        self.test_mutation(
            'calendar_app/services.py',
            'DEFAULT_END_HOUR = 20',
            'DEFAULT_END_HOUR = 19',
            'Mutation 3: Change default end hour from 20 to 19'
        )

        # Mutation 4: Change default time validation (STILL IN FORMS)
        self.test_mutation(
            'calendar_app/forms.py',
            'if start_time == fake_default_time:',
            'if start_time != fake_default_time:',
            'Mutation 4: Invert start time validation logic'
        )

        # Mutation 5: Change query limit (NOW IN SERVICES)
        self.test_mutation(
            'calendar_app/services.py',
            "entries = Unavailability.objects.filter(user=user).order_by('-id')[:limit]",
            "entries = Unavailability.objects.filter(user=user).order_by('-id')[:3]",
            'Mutation 5: Change query limit from variable to hardcoded 3'
        )

        # Mutation 6: Change model string format (STILL IN MODELS)
        self.test_mutation(
            'calendar_app/models.py',
            'return f"{self.user.username}: {self.date} from {self.start_time} to {self.end_time}"',
            'return f"{self.user.username}: {self.date}"',
            'Mutation 6: Remove times from model string representation'
        )

        # Mutation 7: Change comparison operator (NOW IN SERVICES)
        self.test_mutation(
            'calendar_app/services.py',
            'while current < end_dt:',
            'while current <= end_dt:',
            'Mutation 7: Change < to <= in time slot loop'
        )

        # Mutation 8: Change comparison operator in taken slots (NOW IN SERVICES)
        self.test_mutation(
            'calendar_app/services.py',
            'while current < end:',
            'while current <= end:',
            'Mutation 8: Change < to <= in taken slots loop'
        )

        self.print_results()

    def print_results(self):
        """Print mutation testing results"""
        print("\n" + "="*70)
        print("MUTATION TESTING RESULTS")
        print("="*70)

        total = len(self.results['killed']) + len(self.results['survived']) + len(self.results['errors'])

        print(f"\nTotal Mutations Tested: {total}")
        print(f"[KILLED] Tests caught mutation: {len(self.results['killed'])}")
        print(f"[SURVIVED] Tests passed despite mutation: {len(self.results['survived'])}")
        print(f"[ERRORS] Test execution failed: {len(self.results['errors'])}")

        if total > 0:
            mutation_score = (len(self.results['killed']) / total) * 100
            print(f"\nMutation Score: {mutation_score:.1f}%")

        if self.results['survived']:
            print("\nSurvived Mutations (Potential Test Gaps):")
            for mutation in self.results['survived']:
                print(f"  - {mutation}")

        if self.results['errors']:
            print("\nMutations with Errors:")
            for mutation in self.results['errors']:
                print(f"  - {mutation}")

        print("\n" + "="*70)


if __name__ == '__main__':
    # Change to the correct directory
    os.chdir(os.path.dirname(os.path.abspath(__file__)))

    tester = MutationTester()
    tester.run_all_mutations()
