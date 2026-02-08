"""
Session Closeout Validator - Prevents incomplete session closeout.

This module enforces that "complete" means:
1. All changes staged and committed to git
2. Observations logged in observations.jsonl
3. Git status is clean
4. Next session has full context

Usage:
  python -m wai.closeout_validator --check
  python -m wai.closeout_validator --enforce
"""

import sys
import json
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Tuple, List, Dict
import io

# Fix encoding for Windows
if sys.stdout.encoding.lower() in ('cp1252', 'ascii'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')


class CloseoutValidator:
    """Validate that session closeout is truly complete."""
    
    def __init__(self, framework_root: Path = None):
        """Initialize validator.
        
        Args:
            framework_root: Path to framework root (auto-detect if None)
        """
        if not framework_root:
            framework_root = self._find_framework_root()
        
        self.framework_root = framework_root
        self.git_dir = framework_root / '.git'
        self.observations_file = framework_root / 'WAI-Spoke' / 'observations.jsonl'
    
    @staticmethod
    def _find_framework_root() -> Path:
        """Find framework root directory."""
        current = Path.cwd()
        for _ in range(10):
            if (current / 'wai').exists() and (current / '.git').exists():
                return current
            if current == current.parent:
                break
            current = current.parent
        return Path.cwd()
    
    def check_git_status(self) -> Tuple[bool, str]:
        """Check if git working tree is clean.
        
        Returns:
            (is_clean, message)
        """
        try:
            result = subprocess.run(
                ['git', 'status', '--porcelain'],
                cwd=self.framework_root,
                capture_output=True,
                text=True
            )
            
            if result.returncode != 0:
                return False, "Git error: " + result.stderr
            
            if result.stdout.strip():
                lines = result.stdout.strip().split('\n')
                return False, f"Uncommitted changes ({len(lines)} files):\n" + '\n'.join(lines[:5])
            
            return True, "Git status clean"
        except Exception as e:
            return False, f"Git check failed: {e}"
    
    def check_observations_logged(self, session_name: str = None) -> Tuple[bool, str]:
        """Check if today's work is logged in observations.
        
        Args:
            session_name: Session identifier (optional)
        
        Returns:
            (is_logged, message)
        """
        if not self.observations_file.exists():
            return False, "observations.jsonl not found"
        
        try:
            # Check last entry
            with open(self.observations_file) as f:
                lines = f.readlines()
            
            if not lines:
                return False, "observations.jsonl is empty"
            
            # Parse last entry
            last_line = lines[-1].strip()
            last_entry = json.loads(last_line)
            
            # Check if it's recent (today)
            timestamp = last_entry.get('timestamp', '')
            if not timestamp:
                return False, "Last observation missing timestamp"
            
            # Check if from today
            today = datetime.utcnow().strftime('%Y-%m-%d')
            if not timestamp.startswith(today):
                return False, f"Last observation is from {timestamp}, not today"
            
            # Check if marked complete
            status = last_entry.get('status', '')
            if status != '✓ COMPLETE':
                return False, f"Last observation status: {status}, not ✓ COMPLETE"
            
            return True, "Observations logged and marked complete"
        
        except json.JSONDecodeError as e:
            return False, f"Invalid JSON in observations.jsonl: {e}"
        except Exception as e:
            return False, f"Observation check failed: {e}"
    
    def check_git_commit_exists(self, commit_message: str = None) -> Tuple[bool, str]:
        """Check if recent commit exists.
        
        Args:
            commit_message: Expected commit message pattern (optional)
        
        Returns:
            (exists, message)
        """
        try:
            # Get last commit
            result = subprocess.run(
                ['git', 'log', '--oneline', '-1'],
                cwd=self.framework_root,
                capture_output=True,
                text=True
            )
            
            if result.returncode != 0:
                return False, "No commits found"
            
            last_commit = result.stdout.strip()
            if not last_commit:
                return False, "No commits found"
            
            # Extract hash
            commit_hash = last_commit.split()[0]
            
            # Get commit timestamp
            result = subprocess.run(
                ['git', 'log', '-1', '--format=%ai', commit_hash],
                cwd=self.framework_root,
                capture_output=True,
                text=True
            )
            
            timestamp = result.stdout.strip()
            today = datetime.utcnow().strftime('%Y-%m-%d')
            
            if not timestamp.startswith(today):
                return False, f"Latest commit is from {timestamp}, not today"
            
            return True, f"Git commit exists: {commit_hash}"
        
        except Exception as e:
            return False, f"Git commit check failed: {e}"
    
    def validate_all(self) -> Tuple[bool, List[str]]:
        """Validate all closeout requirements.
        
        Returns:
            (all_valid, list_of_checks)
        """
        checks = []
        all_valid = True
        
        # Check 1: Git status clean
        is_clean, msg = self.check_git_status()
        checks.append(('Git Status Clean', is_clean, msg))
        if not is_clean:
            all_valid = False
        
        # Check 2: Git commit exists
        has_commit, msg = self.check_git_commit_exists()
        checks.append(('Git Commit Today', has_commit, msg))
        if not has_commit:
            all_valid = False
        
        # Check 3: Observations logged
        is_logged, msg = self.check_observations_logged()
        checks.append(('Observations Logged', is_logged, msg))
        if not is_logged:
            all_valid = False
        
        return all_valid, checks
    
    def print_validation_report(self) -> bool:
        """Print validation report.
        
        Returns:
            True if all valid, False otherwise
        """
        all_valid, checks = self.validate_all()
        
        print("\n" + "="*70)
        print("SESSION CLOSEOUT VALIDATION REPORT")
        print("="*70)
        
        for check_name, is_valid, message in checks:
            status = "✓ PASS" if is_valid else "✗ FAIL"
            print(f"\n{status} | {check_name}")
            print(f"       {message}")
        
        print("\n" + "="*70)
        if all_valid:
            print("✓ SESSION CLOSEOUT COMPLETE")
            print("  All requirements met. Session is properly closed out.")
        else:
            print("✗ SESSION CLOSEOUT INCOMPLETE")
            print("  Cannot declare session complete until all checks pass.")
            print("\n  Required steps:")
            print("  1. Stage changes:     git add -A")
            print("  2. Commit changes:    git commit -m '...'")
            print("  3. Log observation:   (auto-logged by closeout)")
            print("  4. Verify status:     python -m wai.closeout_validator --check")
        print("="*70 + "\n")
        
        return all_valid
    
    @staticmethod
    def enforce_closeout() -> int:
        """Enforce proper closeout workflow.
        
        Returns:
            Exit code (0 = success, 1 = failure)
        """
        validator = CloseoutValidator()
        
        # Check current state
        all_valid, checks = validator.validate_all()
        
        if all_valid:
            print("✓ Session already properly closed out")
            return 0
        
        # Show what's needed
        print("\n" + "="*70)
        print("SESSION CLOSEOUT - ENFORCED WORKFLOW")
        print("="*70)
        print("\nCurrent status:")
        for check_name, is_valid, message in checks:
            status = "✓" if is_valid else "✗"
            print(f"  {status} {check_name}: {message}")
        
        print("\n" + "-"*70)
        print("\nRequired actions before session can be marked complete:")
        
        # Check 1: Uncommitted changes
        is_clean, msg = validator.check_git_status()
        if not is_clean:
            print("\n1. STAGE AND COMMIT CHANGES")
            print("   Run: git add -A")
            print("   Run: git commit -m 'Session work description...'")
            print(f"   Status: {msg}")
        
        # Check 2: Git commit missing
        has_commit, msg = validator.check_git_commit_exists()
        if not has_commit:
            print("\n2. VERIFY GIT COMMIT")
            print("   Run: git log --oneline -1")
            print(f"   Status: {msg}")
        
        # Check 3: Observations not logged
        is_logged, msg = validator.check_observations_logged()
        if not is_logged:
            print("\n3. LOG OBSERVATIONS")
            print("   Add entry to WAI-Spoke/observations.jsonl")
            print("   Include 'status': '✓ COMPLETE'")
            print(f"   Status: {msg}")
        
        print("\n" + "-"*70)
        print("\nAfter completing these steps, run:")
        print("  python -m wai.closeout_validator --check")
        print("\nOnly declare session complete after validation passes.")
        print("="*70 + "\n")
        
        return 1


def main():
    """Command-line interface."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Validate that session closeout is complete'
    )
    parser.add_argument(
        '--check',
        action='store_true',
        help='Check current closeout status'
    )
    parser.add_argument(
        '--enforce',
        action='store_true',
        help='Enforce closeout workflow (show what\'s needed)'
    )
    
    args = parser.parse_args()
    
    validator = CloseoutValidator()
    
    if args.check or (not args.check and not args.enforce):
        # Default: print validation report
        all_valid = validator.print_validation_report()
        return 0 if all_valid else 1
    
    if args.enforce:
        return validator.enforce_closeout()
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
