"""
Quality Gates for pre-closeout validation.

Ensures code quality before session closeout.
"""

import json
import os
import time
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
import subprocess
import re
from git import Repo, exc as git_exc

from .utils.input import print_info


class QualityGates:
    """Pre-closeout quality validation."""

    def __init__(self, spoke_dir: Path):
        """Initialize quality gates."""
        self.spoke_dir = spoke_dir
        self.wai_spoke_dir = spoke_dir / 'WAI-Spoke'
        self.state_file = self.wai_spoke_dir / 'WAI-State.json'
        self._repo: Optional[Repo] = None

    def _get_repo(self) -> Optional[Repo]:
        """Get GitPython Repo instance."""
        if self._repo is None:
            try:
                self._repo = Repo(self.spoke_dir, search_parent_directories=True)
            except git_exc.InvalidGitRepositoryError:
                return None
        return self._repo

    def _is_ignored_path(self, path: Path) -> bool:
        ignored = {'.git', 'node_modules', '.venv', 'venv', 'dist', 'build'}
        return any(part in ignored for part in path.parts)

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

        # Check for recent successful test run (Optimization)
        skip_reason = self._check_recent_test_run()
        if skip_reason:
            results['skip_reason'] = skip_reason
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

        # Gate 5: Benchmark Regression Testing (if benchmarks exist)
        benchmark_result = self._check_benchmarks()
        results['gates']['benchmarks'] = benchmark_result
        if not benchmark_result['passed']:
            if benchmark_result.get('blocking'):
                results['blockers'].append(benchmark_result['message'])
            else:
                results['warnings'].append(benchmark_result['message'])

        # Gate 6: README.md Accuracy (if README exists)
        readme_result = self._check_readme_sync()
        results['gates']['readme_sync'] = readme_result
        if not readme_result['passed']:
            results['warnings'].append(readme_result['message'])

        return results

    def _check_recent_test_run(self) -> Optional[str]:
        """
        Check if tests passed recently and nothing changed since.

        Returns:
            Skip reason string if gates can be skipped, else None
        """
        log_path = self.wai_spoke_dir / 'WAI-Testing-Log.jsonl'
        if not log_path.exists():
            return None

        try:
            from datetime import datetime, timedelta
            import json

            # Read log to find latest passing run
            with open(log_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            if not lines:
                return None

            latest_pass = None
            for line in reversed(lines):
                try:
                    entry = json.loads(line)
                    if entry.get('status') == 'pass':
                        latest_pass = entry
                        break
                except:
                    continue
            
            if not latest_pass:
                return None

            # Parse timestamp (handle Z suffix)
            pass_ts = latest_pass['timestamp'].replace('Z', '+00:00')
            pass_time = datetime.fromisoformat(pass_ts)
            
            # Ensure we have a timezone-aware current time for comparison
            now = datetime.now(pass_time.tzinfo)

            # 1. Check if within 10 minutes
            if now - pass_time > timedelta(minutes=10):
                return None

            # 2. Check if any tracked files have been modified since the pass
            repo = self._get_repo()
            if not repo:
                return None

            # Get modified and untracked files
            changed = [item.a_path for item in repo.index.diff(None)]
            changed += [item.a_path for item in repo.index.diff("HEAD")]
            untracked = repo.untracked_files

            for f in set(changed + untracked):
                f_path = self.spoke_dir / f
                if f_path.exists():
                    mtime = datetime.fromtimestamp(f_path.stat().st_mtime, pass_time.tzinfo)
                    if mtime > pass_time:
                        return None # Modified after tests

                return (f"✨ Skipping re-test: Quality gates passed recently at {pass_time.strftime('%H:%M:%S')}.\n"
                        f"       (No files modified since then)")

        except Exception:
            # Fallback to running gates if anything goes wrong during check
            return None

    def _check_if_minor_changes(self) -> bool:
        """
        Check if changes are truly minor.

        Returns:
            True if changes are minor (docs only, small tweaks)
        """
        try:
            repo = self._get_repo()
            if not repo:
                return False

            # Get changed files relative to HEAD
            diff_index = repo.index.diff("HEAD")
            changed_files = [item.a_path for item in diff_index]

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
            total_changes = 0
            for diff in diff_index:
                # Basic stat estimation
                if diff.diff:
                    # diff.diff is the actual diff text if available
                    total_changes += len(diff.diff.decode('utf-8', errors='ignore').split('\n'))
            
            # If we couldn't get total_changes from diff text, try summary stats
            if total_changes == 0:
                stats = repo.git.diff("--stat", "HEAD").split('\n')[-1]
                numbers = re.findall(r'(\d+)', stats)
                if numbers:
                    # Sum of insertions and deletions
                    total_changes = sum(int(n) for n in numbers[1:]) # Skip file count

            if total_changes < 10:
                return True

            return False

            return False

        except Exception:
            return False

    def _check_test_coverage(self) -> Dict[str, Any]:
        """
        Check if tests exist and pass.

        Returns:
            Dict with test coverage results
        """
        live_env = os.environ.get("WAI_QG_LIVE", "").strip()
        live_output = live_env not in ("0", "false", "FALSE", "no", "NO")
        timeout_env = os.environ.get("WAI_QG_TIMEOUT", "").strip()
        timeout = 300
        if timeout_env.isdigit():
            timeout = max(60, int(timeout_env))
        # Look for test files
        test_patterns = ['test_*.py', '*_test.py', 'test*.sh', 'smoke-tests-*.sh']
        test_files = []

        for pattern in test_patterns:
            test_files.extend(self.spoke_dir.glob(f"**/{pattern}"))

        test_files = [f for f in test_files if not self._is_ignored_path(f)]

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
                if live_output:
                    print_info(f"    Running: {test_file.name}")
                # Python test
                returncode, output = self._run_command(
                    ['python3', '-m', 'pytest', str(test_file), '-v'],
                    cwd=self.spoke_dir,
                    timeout=timeout,
                    live_output=live_output
                )
                test_results.append({
                    'file': test_file.name,
                    'passed': returncode == 0,
                    'output': "" if live_output else output
                })
            elif test_file.suffix == '.sh':
                if live_output:
                    print_info(f"    Running: {test_file.name}")
                # Shell test
                returncode, output = self._run_command(
                    ['bash', str(test_file)],
                    cwd=self.spoke_dir,
                    timeout=timeout,
                    live_output=live_output
                )
                test_results.append({
                    'file': test_file.name,
                    'passed': returncode == 0,
                    'output': "" if live_output else output
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

    def _run_command(
        self,
        command: List[str],
        cwd: Path,
        timeout: int,
        live_output: bool
    ) -> Tuple[int, str]:
        """Run a command with optional live output and inactivity timeout."""
        if not live_output:
            result = subprocess.run(
                command,
                cwd=cwd,
                capture_output=True,
                text=True,
                timeout=timeout
            )
            output = result.stdout if result.returncode == 0 else result.stderr
            return result.returncode, output or ""

        proc = subprocess.Popen(
            command,
            cwd=cwd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1
        )

        output_lines = []
        last_output = time.time()

        while True:
            line = proc.stdout.readline()
            if line:
                print_info(f"      {line.rstrip()}")
                output_lines.append(line)
                if len(output_lines) > 200:
                    output_lines = output_lines[-200:]
                last_output = time.time()
                continue

            if proc.poll() is not None:
                break

            if time.time() - last_output > timeout:
                proc.terminate()
                try:
                    proc.wait(timeout=5)
                except Exception:
                    proc.kill()
                output_lines.append(f"\n[Timeout after {timeout}s of inactivity]\n")
                return 124, "".join(output_lines)

            time.sleep(0.1)

        return proc.returncode, "".join(output_lines)

    def _check_unit_tests(self) -> Dict[str, Any]:
        """
        Check if unit tests exist for modified code.

        Returns:
            Dict with unit test results
        """
        # Get modified Python files
        try:
            repo = self._get_repo()
            if not repo:
                return {'passed': True, 'message': 'Not a git repository'}

            modified_files = []
            diff_index = repo.index.diff("HEAD")
            for diff in diff_index:
                f = diff.a_path
                if not f.endswith('.py'):
                    continue
                path = Path(f)
                if self._is_ignored_path(path):
                    continue
                name = path.name
                if name.startswith('test_') or name.endswith('_test.py'):
                    continue
                if 'tests' in path.parts:
                    continue
                modified_files.append(f)

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

            # Get recent commit message
            repo = self._get_repo()
            if not repo:
                return {'passed': True, 'message': 'Not a git repository'}

            try:
                recent_commit = repo.head.commit.message.lower()
            except (git_exc.GitCommandError, ValueError):
                return {'passed': True, 'message': 'No prior commits found'}

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

    def _check_benchmarks(self) -> Dict[str, Any]:
        """
        Check if benchmarks pass (no performance regressions).

        Returns:
            Dict with validation results
        """
        benchmark_script = self.spoke_dir / 'scripts' / 'benchmarks' / 'benchmark.py'

        if not benchmark_script.exists():
            # No benchmarks defined - skip this gate
            return {'passed': True, 'message': 'No benchmarks defined (skipped)'}

        print_info("  Running benchmarks...")

        try:
            # Run benchmark with regression detection
            result = subprocess.run(
                ['python3', str(benchmark_script), '--regression'],
                cwd=self.spoke_dir,
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )

            # Check if benchmarks detected regressions
            if result.returncode != 0:
                # Parse output for regression details
                if 'REGRESSIONS DETECTED' in result.stdout or 'regression' in result.stdout.lower():
                    return {
                        'passed': False,
                        'blocking': False,  # Warn but don't block
                        'message': 'Performance regressions detected in benchmarks (review output above)'
                    }
                else:
                    # Benchmark failed for other reasons
                    return {
                        'passed': False,
                        'blocking': False,
                        'message': f'Benchmark execution failed: {result.stderr[:200]}'
                    }

            return {'passed': True, 'message': 'Benchmarks passed - no performance regressions'}

        except subprocess.TimeoutExpired:
            return {
                'passed': False,
                'blocking': False,
                'message': 'Benchmark timeout (>5min) - consider optimizing benchmark suite'
            }
        except Exception as e:
            return {
                'passed': False,
                'blocking': False,
                'message': f'Benchmark error: {str(e)[:100]}'
            }

    def _check_readme_sync(self) -> Dict[str, Any]:
        """
        Check if README.md is in sync with current state.

        Returns:
            Dict with validation results
        """
        readme_path = self.spoke_dir / 'README.md'

        if not readme_path.exists():
            # No README - skip this gate
            return {'passed': True, 'message': 'No README.md found (skipped)'}

        # Check if README was recently updated
        repo = self._get_repo()
        if not repo:
            return {'passed': True, 'message': 'Not a git repo (README check skipped)'}

        try:
            # Get list of modified Python files
            modified_py_files = []
            for item in repo.index.diff(None):
                if item.a_path.endswith('.py'):
                    modified_py_files.append(item.a_path)
            for item in repo.index.diff("HEAD"):
                if item.a_path.endswith('.py'):
                    modified_py_files.append(item.a_path)

            # If code was modified but README wasn't, warn
            if modified_py_files:
                readme_modified = False
                for item in repo.index.diff(None) + repo.index.diff("HEAD"):
                    if 'README.md' in item.a_path:
                        readme_modified = True
                        break

                if not readme_modified:
                    return {
                        'passed': False,
                        'message': f'README.md not updated (code modified: {len(modified_py_files)} files)'
                    }

            # Check if version number in README matches WAI-State.json
            if self.state_file.exists():
                try:
                    state_data = json.loads(self.state_file.read_text())
                    version = state_data.get('wheelwright', {}).get('version', '0.0.0')

                    readme_content = readme_path.read_text()
                    # Look for version patterns in README
                    version_pattern = re.compile(r'[Vv]ersion[:\s]+(\d+\.\d+\.\d+)')
                    matches = version_pattern.findall(readme_content)

                    if matches and version not in matches:
                        return {
                            'passed': False,
                            'message': f'README version mismatch (found {matches[0]}, expected {version})'
                        }

                except Exception:
                    pass  # Skip version check if parsing fails

            return {'passed': True, 'message': 'README.md is up to date'}

        except Exception as e:
            return {
                'passed': False,
                'message': f'README check error: {str(e)[:100]}'
            }
