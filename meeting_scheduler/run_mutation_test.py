"""
Manual Mutation Testing Script
Demonstrates mutation testing by applying mutations to code and running tests
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
                timeout=60
            )
            return result.returncode == 0
        except Exception as e:
            print(f"Error running tests: {e}")
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
        print("MUTATION TESTING")
        print("="*70)

        # Mutation 1: Change time increment in free time calculation
        self.test_mutation(
            'calendar_app/views.py',
            'start_dt += datetime.timedelta(minutes=30)',
            'start_dt += datetime.timedelta(minutes=60)',
            'Mutation 1: Change time slot from 30 to 60 minutes'
        )

        # Mutation 2: Change start time boundary
        self.test_mutation(
            'calendar_app/views.py',
            'start_dt = datetime.datetime.combine(selected_date, datetime.time(8, 0))',
            'start_dt = datetime.datetime.combine(selected_date, datetime.time(9, 0))',
            'Mutation 2: Change start time from 8:00 to 9:00'
        )

        # Mutation 3: Change end time boundary
        self.test_mutation(
            'calendar_app/views.py',
            'end_dt = datetime.datetime.combine(selected_date, datetime.time(20, 0))',
            'end_dt = datetime.datetime.combine(selected_date, datetime.time(19, 0))',
            'Mutation 3: Change end time from 20:00 to 19:00'
        )

        # Mutation 4: Change default time validation
        self.test_mutation(
            'calendar_app/forms.py',
            'if start_time == fake_default_time:',
            'if start_time != fake_default_time:',
            'Mutation 4: Invert start time validation logic'
        )

        # Mutation 5: Change last five query limit
        self.test_mutation(
            'calendar_app/views.py',
            "last_five = Unavailability.objects.order_by('-id')[:5]",
            "last_five = Unavailability.objects.order_by('-id')[:3]",
            'Mutation 5: Change query limit from 5 to 3'
        )

        # Mutation 6: Change model string format
        self.test_mutation(
            'calendar_app/models.py',
            'return f"{self.date} from {self.start_time} to {self.end_time}"',
            'return f"{self.date}"',
            'Mutation 6: Remove times from model string representation'
        )

        # Mutation 7: Change comparison operator
        self.test_mutation(
            'calendar_app/views.py',
            'while start_dt < end_dt:',
            'while start_dt <= end_dt:',
            'Mutation 7: Change < to <= in time slot loop'
        )

        # Mutation 8: Change comparison operator in slot marking
        self.test_mutation(
            'calendar_app/views.py',
            'while current_slot < unavail_end:',
            'while current_slot <= unavail_end:',
            'Mutation 8: Change < to <= in unavailability marking'
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
