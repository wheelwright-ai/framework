"""
Quality Gates for pre-closeout validation.

Ensures code quality before session closeout.
"""

import json
from pathlib import Path
from typing import Dict, Any, List, Optional
import subprocess
import re


class QualityGates:
    """Pre-closeout quality validation."""

    def __init__(self, spoke_dir: Path):
        """Initialize quality gates."""
        self.spoke_dir = spoke_dir
        self.wai_spoke_dir = spoke_dir / 'WAI-Spoke'
        self.state_file = self.wai_spoke_dir / 'WAI-State.json'

    def run_all_gates(self, skip_minor: bool = False) -> Dict[str, Any]:
        """
        Run all quality gates.

        Args:
            skip_minor: Skip validation if changes are truly minor

        Returns:
            Dict with validation results
        """
        results = {
            'passed': True,
            'gates': {},
            'warnings': [],
            'blockers': [],
            'skip_reason': None
        }

        # Check if changes are minor
        if skip_minor:
            is_minor = self._check_if_minor_changes()
            if is_minor:
                results['skip_reason'] = 'Minor changes detected - validation skipped'
                return results

        # Gate 1: Test Coverage
        test_result = self._check_test_coverage()
        results['gates']['test_coverage'] = test_result
        if not test_result['passed']:
            results['passed'] = False
            if test_result.get('blocking'):
                results['blockers'].append(test_result['message'])
            else:
                results['warnings'].append(test_result['message'])

        # Gate 2: Unit Tests Exist
        unit_test_result = self._check_unit_tests()
        results['gates']['unit_tests'] = unit_test_result
        if not unit_test_result['passed']:
            results['passed'] = False
            if unit_test_result.get('blocking'):
                results['blockers'].append(unit_test_result['message'])
            else:
                results['warnings'].append(unit_test_result['message'])

        # Gate 3: Check for Contradictions
        contradiction_result = self._check_contradictions()
        results['gates']['contradictions'] = contradiction_result
        if not contradiction_result['passed']:
            results['passed'] = False
            results['warnings'].append(contradiction_result['message'])

        # Gate 4: Code Smells
        smell_result = self._check_code_smells()
        results['gates']['code_smells'] = smell_result
        if not smell_result['passed']:
            results['warnings'].append(smell_result['message'])

        return results

    def _check_if_minor_changes(self) -> bool:
        """
        Check if changes are truly minor.

        Returns:
            True if changes are minor (docs only, small tweaks)
        """
        try:
            # Get changed files
            result = subprocess.run(
                ['git', 'diff', '--name-only', 'HEAD'],
                cwd=self.spoke_dir,
                capture_output=True,
                text=True
            )

            if result.returncode != 0:
                return False

            changed_files = result.stdout.strip().split('\n')
            changed_files = [f for f in changed_files if f]

            if not changed_files:
                return True  # No changes

            # Check if only docs/comments changed
            code_files_changed = any(
                f.endswith(('.py', '.js', '.ts', '.java', '.go', '.rs'))
                for f in changed_files
            )

            if not code_files_changed:
                return True  # Only docs/config changed

            # Check file sizes (if < 10 lines changed total, it's minor)
            result = subprocess.run(
                ['git', 'diff', '--stat'],
                cwd=self.spoke_dir,
                capture_output=True,
                text=True
            )

            if result.returncode == 0:
                # Parse stat output
                lines = result.stdout.split('\n')
                for line in lines:
                    if 'insertions' in line or 'deletions' in line:
                        # Extract numbers
                        numbers = re.findall(r'(\d+) insertion|(\d+) deletion', line)
                        total_changes = sum(int(n[0] or n[1]) for n in numbers)
                        if total_changes < 10:
                            return True

            return False

        except Exception:
            return False

    def _check_test_coverage(self) -> Dict[str, Any]:
        """
        Check if tests exist and pass.

        Returns:
            Dict with test coverage results
        """
        # Look for test files
        test_patterns = ['test_*.py', '*_test.py', 'test*.sh', 'smoke-tests-*.sh']
        test_files = []

        for pattern in test_patterns:
            test_files.extend(self.spoke_dir.glob(f"**/{pattern}"))

        if not test_files:
            return {
                'passed': False,
                'blocking': False,
                'message': 'No test files found. Consider adding tests for new features.',
                'test_files': []
            }

        # Try to run tests
        test_results = []
        for test_file in test_files:
            if test_file.suffix == '.py':
                # Python test
                result = subprocess.run(
                    ['python3', '-m', 'pytest', str(test_file), '-v'],
                    cwd=self.spoke_dir,
                    capture_output=True,
                    text=True,
                    timeout=120
                )
                test_results.append({
                    'file': test_file.name,
                    'passed': result.returncode == 0,
                    'output': result.stdout if result.returncode == 0 else result.stderr
                })
            elif test_file.suffix == '.sh':
                # Shell test
                result = subprocess.run(
                    ['bash', str(test_file)],
                    cwd=self.spoke_dir,
                    capture_output=True,
                    text=True,
                    timeout=120
                )
                test_results.append({
                    'file': test_file.name,
                    'passed': result.returncode == 0,
                    'output': result.stdout if result.returncode == 0 else result.stderr
                })

        # Analyze results
        all_passed = all(t['passed'] for t in test_results)
        failed_tests = [t for t in test_results if not t['passed']]

        if not all_passed:
            return {
                'passed': False,
                'blocking': True,
                'message': f"{len(failed_tests)} test file(s) failed. Fix tests before closeout.",
                'failed_tests': failed_tests,
                'test_files': [str(f) for f in test_files]
            }

        return {
            'passed': True,
            'message': f"All {len(test_files)} test file(s) passed.",
            'test_files': [str(f) for f in test_files]
        }

    def _check_unit_tests(self) -> Dict[str, Any]:
        """
        Check if unit tests exist for modified code.

        Returns:
            Dict with unit test results
        """
        # Get modified Python files
        try:
            result = subprocess.run(
                ['git', 'diff', '--name-only', 'HEAD'],
                cwd=self.spoke_dir,
                capture_output=True,
                text=True
            )

            if result.returncode != 0:
                return {'passed': True, 'message': 'Unable to check git diff'}

            modified_files = [
                f for f in result.stdout.strip().split('\n')
                if f.endswith('.py')
                and not f.startswith('test_')
                and not f.endswith('_test.py')
                and not f.startswith('tests/')
            ]

            if not modified_files:
                return {'passed': True, 'message': 'No Python files modified'}

            # Check if corresponding test files exist
            missing_tests = []
            for py_file in modified_files:
                # Look for test_<file>.py or <file>_test.py
                file_path = Path(py_file)
                test_name1 = file_path.parent / f"test_{file_path.name}"
                test_name2 = file_path.parent / f"{file_path.stem}_test.py"

                if not test_name1.exists() and not test_name2.exists():
                    missing_tests.append(py_file)

            if missing_tests:
                return {
                    'passed': False,
                    'blocking': False,
                    'message': f"{len(missing_tests)} modified file(s) lack unit tests: {', '.join(missing_tests)}",
                    'missing_tests': missing_tests
                }

            return {'passed': True, 'message': 'All modified Python files have tests'}

        except Exception as e:
            return {'passed': True, 'message': f'Unable to check unit tests: {e}'}

    def _check_contradictions(self) -> Dict[str, Any]:
        """
        Check for contradictions with existing decisions.

        Returns:
            Dict with contradiction check results
        """
        try:
            with open(self.state_file) as f:
                state = json.load(f)

            decisions = state.get('decisions', [])

            if not decisions:
                return {'passed': True, 'message': 'No prior decisions to check'}

            # Get recent commit messages
            result = subprocess.run(
                ['git', 'log', '-1', '--pretty=%B'],
                cwd=self.spoke_dir,
                capture_output=True,
                text=True
            )

            if result.returncode != 0:
                return {'passed': True, 'message': 'Unable to check contradictions'}

            recent_commit = result.stdout.lower()

            # Check for reversal keywords
            reversal_keywords = ['revert', 'undo', 'remove', 'delete', 'reverse']
            has_reversal = any(keyword in recent_commit for keyword in reversal_keywords)

            if has_reversal:
                # Check if this contradicts a high-impact decision
                high_impact_decisions = [d for d in decisions if d.get('impact', 0) >= 8]

                if high_impact_decisions:
                    return {
                        'passed': False,
                        'message': f"Commit may contradict {len(high_impact_decisions)} high-impact decision(s). Review before closeout.",
                        'decisions': high_impact_decisions[:3]
                    }

            return {'passed': True, 'message': 'No contradictions detected'}

        except Exception:
            return {'passed': True, 'message': 'Unable to check contradictions'}

    def _check_code_smells(self) -> Dict[str, Any]:
        """
        Check for code smells.

        Returns:
            Dict with code smell results
        """
        smells = []

        # Check for large files
        for py_file in self.spoke_dir.glob('**/*.py'):
            if 'venv' in str(py_file) or '.git' in str(py_file):
                continue

            line_count = len(py_file.read_text().split('\n'))

            if line_count > 500:
                smells.append(f"{py_file.name} is {line_count} lines (consider refactoring)")

        if smells:
            return {
                'passed': False,
                'message': f"Code smells detected: {', '.join(smells)}",
                'smells': smells
            }

        return {'passed': True, 'message': 'No code smells detected'}

    def generate_uat_instructions(self, feature_description: str) -> str:
        """
        Generate UAT instructions for a feature.

        Args:
            feature_description: Description of the implemented feature

        Returns:
            UAT instruction text
        """
        return f"""# User Acceptance Testing - {feature_description}

## Pre-Test Checklist
- [ ] All unit tests pass
- [ ] Code reviewed
- [ ] No merge conflicts

## Test Scenarios

### Scenario 1: Happy Path
**Steps:**
1. [Add specific steps here]
2. [Expected result]

### Scenario 2: Edge Cases
**Steps:**
1. [Add edge case steps]
2. [Expected result]

### Scenario 3: Error Handling
**Steps:**
1. [Add error scenario]
2. [Expected error handling]

## Acceptance Criteria
- [ ] Feature works as described
- [ ] No regression in existing functionality
- [ ] Performance is acceptable
- [ ] Error messages are clear

## Sign-off
- Tested by: ___________
- Date: ___________
- Status: [ ] PASS [ ] FAIL
"""
