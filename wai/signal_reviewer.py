"""
Signal Reviewer - /wai-learn command implementation

Allows users to review and acknowledge cross-node signals from hub/intake/.
"""

import json
from pathlib import Path
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional


class SignalReviewer:
    """Handles signal review and acknowledgment workflow."""

    def __init__(self, hub_path: str):
        """
        Initialize signal reviewer.

        Args:
            hub_path: Path to hub directory
        """
        self.hub_path = Path(hub_path)
        self.intake_dir = self.hub_path / "intake"
        self.archive_dir = self.hub_path / "archive"
        self.health_file = self.hub_path / "health.yaml"

    def list_pending_signals(self) -> List[Dict[str, Any]]:
        """
        List all pending signals in hub/intake/.

        Returns:
            List of signal dicts
        """
        if not self.intake_dir.exists():
            return []

        signals = []
        for signal_file in self.intake_dir.glob("*.lug.json"):
            with open(signal_file) as f:
                signal = json.load(f)
                signal['_file'] = signal_file.name
                signals.append(signal)

        # Sort by impact (descending), then timestamp (newest first)
        signals.sort(key=lambda s: (-s['impact'], s['timestamp']), reverse=False)

        return signals

    def display_signal(self, signal: Dict[str, Any], index: int, total: int) -> None:
        """
        Display a signal for review.

        Args:
            signal: Signal dict
            index: Current signal index (1-based)
            total: Total number of signals
        """
        print(f"\n{'='*60}")
        print(f"Signal {index} of {total}")
        print(f"{'='*60}")
        print(f"\nTitle: {signal['title']}")
        print(f"Source: {signal['source_spoke']}")
        print(f"Impact: {signal['impact']}/10")
        print(f"Created: {signal['timestamp']}")
        print(f"Tags: {', '.join(signal.get('tags', []))}")

        print(f"\nBody:")
        print(f"{signal['body']}")

        if 'pev' in signal:
            pev = signal['pev']
            print(f"\nPEV:")
            print(f"  Perceive: {pev.get('perceive', 'N/A')}")
            print(f"  Execute: {pev.get('execute', 'N/A')}")
            print(f"  Verify: {pev.get('verify', 'N/A')}")

    def prompt_action(self) -> str:
        """
        Prompt user for action on current signal.

        Returns:
            Action code: 'adopt', 'acknowledge', 'skip', 'quit'
        """
        print("\nActions:")
        print("  [A] Adopt this pattern (create local Lug + archive)")
        print("  [K] Acknowledge only (mark reviewed, archive)")
        print("  [S] Skip (leave in queue for later)")
        print("  [Q] Quit review")

        while True:
            choice = input("\nChoice: ").strip().upper()
            if choice in ['A', 'K', 'S', 'Q']:
                action_map = {
                    'A': 'adopt',
                    'K': 'acknowledge',
                    'S': 'skip',
                    'Q': 'quit'
                }
                return action_map[choice]
            print("Invalid choice. Please enter A, K, S, or Q.")

    def adopt_signal(self, signal: Dict[str, Any], spoke_lugs_file: Path) -> str:
        """
        Adopt signal - create local Lug referencing signal.

        Args:
            signal: Signal dict
            spoke_lugs_file: Path to spoke's WAI-Lugs.jsonl

        Returns:
            Local Lug ID created
        """
        # Create local Lug referencing the signal
        local_lug = {
            "lug_id": f"adopted-{signal['lug_id']}",
            "type": "decision",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "title": f"Adopted pattern: {signal['title']}",
            "body": f"Adopted cross-node signal from {signal['source_spoke']}. "
                    f"Original: {signal['body']}",
            "tags": signal.get('tags', []) + ["adopted", "cross-node"],
            "impact": signal['impact'],
            "status": "resolved",
            "resolution_reason": f"Adopted from hub signal: {signal['lug_id']}",
            "extras": {
                "adopted_from": signal['lug_id'],
                "source_spoke": signal['source_spoke']
            },
            "created_by": "wai-learn"
        }

        # Append to spoke Lugs
        with open(spoke_lugs_file, 'a') as f:
            f.write(json.dumps(local_lug) + '\n')

        return local_lug['lug_id']

    def archive_signal(self, signal: Dict[str, Any], action: str) -> Path:
        """
        Archive signal - move from intake/ to archive/{YYYY-MM}/.

        Args:
            signal: Signal dict
            action: Action taken ('adopted' or 'acknowledged')

        Returns:
            Path to archived signal file
        """
        # Create archive directory for this month
        now = datetime.now(timezone.utc)
        month_dir = self.archive_dir / f"{now.year}-{now.month:02d}"
        month_dir.mkdir(parents=True, exist_ok=True)

        # Add archive metadata to signal
        signal['_archived'] = {
            "archived_at": now.isoformat(),
            "action_taken": action
        }

        # Write to archive
        archive_file = month_dir / signal['_file']
        with open(archive_file, 'w') as f:
            json.dump(signal, f, indent=2)

        # Remove from intake
        intake_file = self.intake_dir / signal['_file']
        intake_file.unlink()

        return archive_file

    def update_health(self, pending_count: int) -> None:
        """
        Update hub/health.yaml with new pending count.

        Args:
            pending_count: Current number of pending signals
        """
        if not self.health_file.exists():
            return

        with open(self.health_file, 'r') as f:
            content = f.read()

        # Simple replacement (could use YAML parser for robustness)
        import re
        content = re.sub(r'pending_count: \d+', f'pending_count: {pending_count}', content)

        with open(self.health_file, 'w') as f:
            f.write(content)

    def review_signals(self, spoke_lugs_file: Optional[Path] = None) -> Dict[str, int]:
        """
        Main review workflow - iterate through pending signals.

        Args:
            spoke_lugs_file: Path to spoke's WAI-Lugs.jsonl (for adoption)

        Returns:
            Summary dict: {adopted: N, acknowledged: N, skipped: N}
        """
        signals = self.list_pending_signals()

        if not signals:
            print("\n✅ No pending signals to review")
            return {"adopted": 0, "acknowledged": 0, "skipped": 0}

        print(f"\n📨 Found {len(signals)} pending signal(s)")

        summary = {"adopted": 0, "acknowledged": 0, "skipped": 0}

        for i, signal in enumerate(signals, 1):
            self.display_signal(signal, i, len(signals))
            action = self.prompt_action()

            if action == 'quit':
                print("\n⏸️  Review paused. Remaining signals left in queue.")
                break
            elif action == 'skip':
                print("⏭️  Skipped - signal remains in queue")
                summary["skipped"] += 1
            elif action == 'adopt':
                if spoke_lugs_file:
                    local_lug_id = self.adopt_signal(signal, spoke_lugs_file)
                    print(f"✅ Adopted - created local Lug: {local_lug_id}")
                    archive_file = self.archive_signal(signal, "adopted")
                    print(f"📦 Archived to: {archive_file}")
                    summary["adopted"] += 1
                else:
                    print("⚠️  Cannot adopt - no spoke Lugs file specified")
                    print("   Acknowledging instead...")
                    archive_file = self.archive_signal(signal, "acknowledged")
                    print(f"📦 Archived to: {archive_file}")
                    summary["acknowledged"] += 1
            elif action == 'acknowledge':
                archive_file = self.archive_signal(signal, "acknowledged")
                print(f"✅ Acknowledged")
                print(f"📦 Archived to: {archive_file}")
                summary["acknowledged"] += 1

        # Update hub health
        remaining = len(self.list_pending_signals())
        self.update_health(remaining)
        print(f"\n📊 Hub health updated: {remaining} signal(s) remaining")

        return summary


def main():
    """Command-line entry point for /wai-learn."""
    import sys
    from pathlib import Path

    # Find hub path (check common locations)
    hub_paths = [
        Path.cwd().parent / "hub",
        Path.cwd() / ".." / "hub",
        Path("/home/mario/projects/wheelwright-ai/hub")
    ]

    hub_path = None
    for path in hub_paths:
        if path.exists():
            hub_path = path
            break

    if not hub_path:
        print("❌ Error: Could not find hub directory")
        print("   Searched:", hub_paths)
        sys.exit(1)

    # Find spoke Lugs file
    spoke_lugs_paths = [
        Path.cwd() / "WAI-Spoke" / "WAI-Lugs.jsonl",
        Path.cwd() / "registry" / "wheelwright" / "framework" / "WAI-Lugs.jsonl"
    ]

    spoke_lugs_file = None
    for path in spoke_lugs_paths:
        if path.exists():
            spoke_lugs_file = path
            break

    print("╔════════════════════════════════════════╗")
    print("║       WAI Cross-Node Signal Review     ║")
    print("╚════════════════════════════════════════╝")

    reviewer = SignalReviewer(str(hub_path))
    summary = reviewer.review_signals(spoke_lugs_file)

    print("\n" + "="*60)
    print("Review Summary:")
    print(f"  Adopted: {summary['adopted']}")
    print(f"  Acknowledged: {summary['acknowledged']}")
    print(f"  Skipped: {summary['skipped']}")
    print("="*60)


if __name__ == "__main__":
    main()
