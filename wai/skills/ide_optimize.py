"""
IDE Optimization Advisor - Check if IDE settings match machine capabilities.

This skill analyzes the current machine profile and compares it with IDE
settings to identify optimization opportunities.

Usage:
    wai check-ide-optimization [--fix] [--verbose]
"""

import json
from pathlib import Path
from typing import Dict, Any, List, Tuple, Optional
from datetime import datetime, timezone

from .machine_detect import MachineDetector


class IDEOptimizationAdvisor:
    """Analyze IDE settings against machine capabilities."""

    def __init__(self, project_root: Path):
        self.project_root = Path(project_root)
        self.vscode_settings = self.project_root / '.vscode' / 'settings.json'
        self.detector = MachineDetector()

    def load_machine_profile(self) -> Optional[Dict[str, Any]]:
        """Load machine profile from hub or detect."""
        hub_path = self.project_root.parent / 'hub' / 'machines' / f'{self.detector.hostname}.lug.json'

        if hub_path.exists():
            with open(hub_path, 'r') as f:
                return json.load(f)

        # Create profile if it doesn't exist
        return self.detector.create_lug(save_path=hub_path)

    def load_current_settings(self) -> Dict[str, Any]:
        """Load current VS Code settings."""
        if not self.vscode_settings.exists():
            return {}

        with open(self.vscode_settings, 'r') as f:
            content = f.read()
            # Strip comments for JSON parsing
            lines = []
            for line in content.split('\n'):
                if not line.strip().startswith('//'):
                    lines.append(line)
            return json.loads('\n'.join(lines))

    def analyze_optimization_gaps(self) -> List[Dict[str, Any]]:
        """Identify gaps between current settings and recommendations."""
        profile = self.load_machine_profile()
        current = self.load_current_settings()

        if not profile:
            return [{
                'level': 'error',
                'category': 'profile',
                'message': 'No machine profile found. Run wai detect-machine --save-to-hub',
                'fix': None
            }]

        gaps = []
        classification = profile['machine']['classification']
        recommended = profile['recommended_settings']['vscode']

        # Check each recommended setting
        for key, rec_value in recommended.items():
            current_value = current.get(key)

            if current_value != rec_value:
                gaps.append({
                    'level': 'warning' if classification == 'high-performance' else 'info',
                    'category': 'vscode',
                    'setting': key,
                    'current': current_value,
                    'recommended': rec_value,
                    'reason': self._get_reason(key, rec_value, classification),
                    'impact': self._get_impact(key, classification)
                })

        # Check for unoptimized patterns
        gaps.extend(self._check_patterns(current, classification))

        return gaps

    def _get_reason(self, setting: str, value: Any, classification: str) -> str:
        """Get reason for recommendation."""
        reasons = {
            'python.analysis.typeCheckingMode': {
                'strict': f"With {classification} hardware, strict type checking improves code quality without performance cost",
                'basic': "For lower-spec machines, basic type checking balances features and performance"
            },
            'python.analysis.diagnosticMode': {
                'workspace': f"Your {classification} machine can handle full workspace analysis for better error detection",
                'openFilesOnly': "Limited to open files to conserve resources on lower-spec machines"
            },
            'editor.minimap.enabled': {
                True: "Your GPU and RAM can easily handle minimap rendering for better navigation",
                False: "Minimap disabled to reduce rendering overhead on lower-spec machines"
            },
            'git.autorefresh': {
                True: "Your CPU can spare cycles for automatic git status updates",
                False: "Manual refresh conserves CPU on lower-spec machines"
            }
        }

        return reasons.get(setting, {}).get(str(value), f"Optimized for {classification} machines")

    def _get_impact(self, setting: str, classification: str) -> str:
        """Get impact description."""
        if classification == 'high-performance':
            impacts = {
                'python.analysis.typeCheckingMode': 'High - Better type safety and refactoring',
                'python.analysis.diagnosticMode': 'High - Catch errors before running code',
                'editor.minimap.enabled': 'Medium - Easier navigation in large files',
                'git.autorefresh': 'Low - Convenience feature'
            }
        else:
            impacts = {
                'python.analysis.typeCheckingMode': 'Medium - Reduced CPU usage',
                'python.analysis.diagnosticMode': 'High - Significantly faster editor',
                'editor.minimap.enabled': 'Medium - Reduced memory usage',
                'git.autorefresh': 'Low - Slight CPU savings'
            }

        return impacts.get(setting, 'Medium')

    def _check_patterns(self, settings: Dict[str, Any], classification: str) -> List[Dict[str, Any]]:
        """Check for common optimization patterns."""
        issues = []

        # Pattern 1: High-performance machine with conservative settings
        if classification == 'high-performance':
            if settings.get('python.analysis.memory.keepLibraryAst') == False:
                issues.append({
                    'level': 'warning',
                    'category': 'pattern',
                    'pattern': 'conservative-on-powerful-hardware',
                    'message': 'Conservative Python settings detected on high-performance machine',
                    'recommendation': 'Enable keepLibraryAst for faster intellisense',
                    'impact': 'High - Much faster code completion and hover info'
                })

        # Pattern 2: Low-power machine with aggressive settings
        if classification == 'low-power':
            if settings.get('python.analysis.diagnosticMode') == 'workspace':
                issues.append({
                    'level': 'warning',
                    'category': 'pattern',
                    'pattern': 'aggressive-on-low-power',
                    'message': 'Resource-intensive Python settings detected on low-power machine',
                    'recommendation': 'Set diagnosticMode to openFilesOnly',
                    'impact': 'High - Editor will be much more responsive'
                })

        # Pattern 3: Missing file watching exclusions
        watcher_exclude = settings.get('files.watcherExclude', {})
        if len(watcher_exclude) < 5:
            issues.append({
                'level': 'info',
                'category': 'pattern',
                'pattern': 'insufficient-exclusions',
                'message': 'Few file watcher exclusions - may watch unnecessary files',
                'recommendation': 'Add exclusions for __pycache__, .git, etc.',
                'impact': 'Medium - Reduced CPU and memory usage'
            })

        return issues

    def generate_report(self, verbose: bool = False) -> str:
        """Generate optimization report."""
        profile = self.load_machine_profile()
        gaps = self.analyze_optimization_gaps()

        if not profile:
            return "❌ No machine profile found. Run: wai detect-machine --save-to-hub"

        lines = []
        lines.append(f"\n🔍 IDE Optimization Analysis")
        lines.append(f"{'=' * 60}")
        lines.append(f"Machine: {profile['machine']['id']}")
        lines.append(f"Classification: {profile['machine']['classification'].upper()}")
        lines.append(f"CPU: {profile['machine']['specs']['cpu']['model']}")
        lines.append(f"RAM: {profile['machine']['specs']['memory']['total_gb']} GB")
        lines.append(f"\n📊 Analysis Results:")
        lines.append(f"   Total gaps found: {len(gaps)}")

        if not gaps:
            lines.append(f"\n✅ Your IDE is fully optimized for this machine!")
            return '\n'.join(lines)

        # Group by level
        errors = [g for g in gaps if g['level'] == 'error']
        warnings = [g for g in gaps if g['level'] == 'warning']
        info = [g for g in gaps if g['level'] == 'info']

        if errors:
            lines.append(f"\n❌ ERRORS ({len(errors)}):")
            for gap in errors:
                lines.append(f"   • {gap['message']}")

        if warnings:
            lines.append(f"\n⚠️  WARNINGS ({len(warnings)}):")
            for gap in warnings:
                if 'setting' in gap:
                    lines.append(f"   • {gap['setting']}")
                    lines.append(f"     Current: {gap['current']}")
                    lines.append(f"     Recommended: {gap['recommended']}")
                    lines.append(f"     Impact: {gap['impact']}")
                    if verbose:
                        lines.append(f"     Reason: {gap['reason']}")
                else:
                    lines.append(f"   • {gap['message']}")
                    lines.append(f"     {gap['recommendation']}")
                    lines.append(f"     Impact: {gap['impact']}")
                lines.append("")

        if info and verbose:
            lines.append(f"\nℹ️  INFO ({len(info)}):")
            for gap in info:
                lines.append(f"   • {gap.get('message', gap.get('setting'))}")

        lines.append(f"\n💡 Next Steps:")
        lines.append(f"   1. Review warnings above")
        lines.append(f"   2. Run with --fix to auto-apply recommendations")
        lines.append(f"   3. Or manually update .vscode/settings.json")

        return '\n'.join(lines)

    def apply_fixes(self, silent: bool = False) -> int:
        """Apply recommended fixes to settings.json.

        Args:
            silent: If True, don't print messages (for automatic application)
        """
        profile = self.load_machine_profile()
        if not profile:
            if not silent:
                print("❌ No machine profile found")
            return 1

        current = self.load_current_settings()
        recommended = profile['recommended_settings']['vscode']

        # Merge recommendations into current settings
        updated = {**current, **recommended}

        # Add metadata comment
        self.vscode_settings.parent.mkdir(parents=True, exist_ok=True)

        with open(self.vscode_settings, 'w') as f:
            f.write('{\n')
            f.write(f'  // Auto-optimized by WAI for {profile["machine"]["id"]}\n')
            f.write(f'  // Classification: {profile["machine"]["classification"]}\n')
            f.write(f'  // Generated: {datetime.now(timezone.utc).isoformat()}\n')
            f.write('  \n')

            # Write settings
            items = list(updated.items())
            for i, (key, value) in enumerate(items):
                json_value = json.dumps(value)
                comma = ',' if i < len(items) - 1 else ''
                f.write(f'  "{key}": {json_value}{comma}\n')

            f.write('}\n')

        # Update optimization history in lug
        self._update_optimization_history(profile)

        if not silent:
            print(f"✅ Applied optimizations to {self.vscode_settings}")
        return 0

    def _update_optimization_history(self, profile: Dict[str, Any]) -> None:
        """Update the optimization history in the machine profile lug."""
        hub_path = self.project_root.parent / 'hub' / 'machines' / f'{self.detector.hostname}.lug.json'

        if not hub_path.exists():
            return

        # Get relative project path
        try:
            project_path = str(self.project_root.relative_to(Path.home()))
        except ValueError:
            project_path = str(self.project_root)

        # Update history
        if 'optimization_history' not in profile:
            profile['optimization_history'] = {
                'projects_optimized': [],
                'total_optimizations': 0
            }

        history = profile['optimization_history']
        now = datetime.now(timezone.utc).isoformat()
        history['last_check'] = now
        history['last_applied'] = now

        if project_path not in history.get('projects_optimized', []):
            if 'projects_optimized' not in history:
                history['projects_optimized'] = []
            history['projects_optimized'].append(project_path)

        history['total_optimizations'] = history.get('total_optimizations', 0) + 1

        # Write back to lug
        with open(hub_path, 'w') as f:
            json.dump(profile, f, indent=2)

    def check_and_auto_apply(self, silent: bool = False) -> bool:
        """Check if optimization needed and auto-apply if so.

        Returns:
            True if optimizations were applied, False otherwise
        """
        gaps = self.analyze_optimization_gaps()

        # Filter out info-level gaps
        significant_gaps = [g for g in gaps if g['level'] in ('error', 'warning')]

        if significant_gaps:
            if not silent:
                print(f"⚙️  Optimizing IDE for {self.detector.hostname}...")
            self.apply_fixes(silent=True)
            if not silent:
                print(f"✅ Applied {len(significant_gaps)} optimizations")
            return True

        return False


def main():
    """CLI entry point."""
    import sys

    project_root = Path.cwd()
    advisor = IDEOptimizationAdvisor(project_root)

    # Auto-apply is now the default behavior
    if '--check-only' in sys.argv:
        # Just check, don't apply
        verbose = '--verbose' in sys.argv or '-v' in sys.argv
        report = advisor.generate_report(verbose=verbose)
        print(report)

        gaps = advisor.analyze_optimization_gaps()
        errors = [g for g in gaps if g['level'] == 'error']
        return 1 if errors else 0

    # Default: auto-apply optimizations
    verbose = '--verbose' in sys.argv or '-v' in sys.argv
    silent = '--silent' in sys.argv

    if advisor.check_and_auto_apply(silent=silent):
        if verbose:
            report = advisor.generate_report(verbose=True)
            print(report)
        return 0
    else:
        if not silent:
            print(f"✅ IDE already optimized for {advisor.detector.hostname}")
        return 0


if __name__ == '__main__':
    exit(main())
