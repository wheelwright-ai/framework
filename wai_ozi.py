#!/usr/bin/env python3
"""Ozi - Chief of Staff work queue monitor."""

import argparse
import json
import os
import re
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List


class OziWorkQueueMonitor:
    """Monitor shared lugs with session-local auto mode."""

    AUTO_EXCLUDED_TYPES = {"implementation", "epic", "review", "session-summary"}

    def __init__(self, spoke_path: str = "WAI-Spoke"):
        self.spoke_path = Path(spoke_path)
        self.bytype_dir = self.spoke_path / "lugs" / "bytype"
        self.changelog_file = self.spoke_path / "WAI-Changelog.jsonl"
        self.skills_file = self.spoke_path / "WAI-Skills.jsonl"
        self.runtime_dir = self.spoke_path / "runtime" / "ozi-sessions"
        self.runtime_dir.mkdir(parents=True, exist_ok=True)

    def is_enabled(self) -> bool:
        try:
            with open(self.skills_file, "r") as handle:
                for line in handle:
                    skill = json.loads(line)
                    if skill.get("id") == "ozi-work-queue-monitor":
                        return skill.get(
                            "enabled", skill.get("enabled_by_default", False)
                        )
        except (FileNotFoundError, json.JSONDecodeError):
            pass
        return False

    def session_key(self) -> str:
        raw = (
            os.environ.get("WAI_OZI_SESSION_KEY")
            or os.environ.get("ZELLIJ_SESSION_NAME")
            or os.environ.get("WT_SESSION")
            or "interactive"
        )
        sanitized = re.sub(r"[^A-Za-z0-9._-]+", "-", raw).strip("-")
        return sanitized or "interactive"

    def runtime_config_path(self) -> Path:
        return self.runtime_dir / f"{self.session_key()}.json"

    def load_runtime_config(self) -> Dict[str, Any]:
        path = self.runtime_config_path()
        if not path.exists():
            return {
                "session_key": self.session_key(),
                "auto_mode": False,
                "max_parallel": 1,
                "watch_mode": True,
                "poll_interval_minutes": 5,
                "updated_at": None,
            }
        try:
            with open(path, "r") as handle:
                config = json.load(handle)
        except (FileNotFoundError, json.JSONDecodeError):
            config = {}
        config.setdefault("session_key", self.session_key())
        config.setdefault("auto_mode", False)
        config.setdefault("max_parallel", 1)
        config.setdefault("watch_mode", True)
        config.setdefault("poll_interval_minutes", 5)
        config.setdefault("updated_at", None)
        return config

    def save_runtime_config(self, config: Dict[str, Any]) -> None:
        config["session_key"] = self.session_key()
        config["updated_at"] = datetime.now(timezone.utc).isoformat()
        with open(self.runtime_config_path(), "w") as handle:
            json.dump(config, handle, indent=2)

    def is_auto_mode_enabled(self) -> bool:
        return bool(self.load_runtime_config().get("auto_mode", False))

    def current_owner_name(self) -> str:
        return f"ozi:{self.session_key()}"

    def _scan_bytype_folders(self, statuses: List[str]) -> List[Dict[str, Any]]:
        """Scan bytype/ folders for lugs matching given statuses."""
        results: List[Dict[str, Any]] = []
        if not self.bytype_dir.exists():
            return results
        for type_dir in sorted(self.bytype_dir.iterdir()):
            if not type_dir.is_dir():
                continue
            for status_name in statuses:
                status_path = type_dir / status_name
                if not status_path.exists():
                    continue
                for lug_file in sorted(status_path.glob("*.json")):
                    try:
                        lug = json.loads(lug_file.read_text())
                        # Ensure essential fields from filesystem context
                        lug.setdefault("id", lug_file.stem)
                        lug.setdefault("type", type_dir.name)
                        lug["_file_path"] = str(lug_file)
                        lug["_fs_status"] = status_name
                        lug["_fs_type"] = type_dir.name
                        results.append(lug)
                    except (json.JSONDecodeError, OSError):
                        continue
        return results

    def scan_work_queue(self) -> Dict[str, List[Dict[str, Any]]]:
        queue: Dict[str, List[Dict[str, Any]]] = {
            "ready": [],
            "claimed_by_me": [],
            "in_progress": [],
            "ready_for_recheck": [],
            "accepted": [],
            "needs_clarification": [],
            "stale": [],
            "completed_recently": [],
        }

        now = datetime.now(timezone.utc)
        owner_name = self.current_owner_name()

        # Scan open + in_progress lugs from bytype/ filesystem
        all_lugs = self._scan_bytype_folders(["open", "in_progress"])

        for lug in all_lugs:
            # Use lug's own status field if present, fall back to filesystem status
            status = lug.get("status", lug.get("s", lug.get("_fs_status", "open")))
            # Normalize short codes
            if status in ("o", "open"):
                status = "open"
            elif status in ("p", "in-progress", "in_progress"):
                status = "in_progress"

            workflow = lug.get("workflow", {})
            owner = workflow.get("current_owner")

            # Open items are ready for work
            if status == "open":
                queue["ready"].append(lug)
                continue

            if status == "in_progress":
                if owner == owner_name:
                    queue["claimed_by_me"].append(lug)
                updated_at = workflow.get("updated_at")
                if updated_at:
                    try:
                        updated_dt = datetime.fromisoformat(
                            updated_at.replace("Z", "+00:00")
                        )
                        if (now - updated_dt) > timedelta(hours=4):
                            queue["stale"].append(lug)
                        else:
                            queue["in_progress"].append(lug)
                    except ValueError:
                        queue["in_progress"].append(lug)
                else:
                    queue["in_progress"].append(lug)
                continue

            if status == "ready_for_recheck":
                queue["ready_for_recheck"].append(lug)
                continue

            if status == "needs_clarification":
                queue["needs_clarification"].append(lug)

        return queue

    def _age_string(self, value: str) -> str:
        try:
            dt_value = datetime.fromisoformat(value.replace("Z", "+00:00"))
            delta = datetime.now(timezone.utc) - dt_value
        except ValueError:
            return "recently"
        minutes = max(0, int(delta.total_seconds() // 60))
        if minutes < 60:
            return f"{minutes}min ago"
        return f"{minutes // 60}hr ago"

    def generate_briefing(self, queue: Dict[str, List[Dict[str, Any]]]) -> str:
        if self.is_auto_mode_enabled():
            return self._generate_auto_mode_briefing(queue)
        return self._generate_interactive_briefing(queue)

    def _generate_interactive_briefing(
        self, queue: Dict[str, List[Dict[str, Any]]]
    ) -> str:
        lines = [
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
            "👔 OZI'S BRIEFING",
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
            "",
            f"Hello! Session key: {self.session_key()}",
            "",
        ]

        needs_attention = queue["needs_clarification"] + queue["accepted"]
        if needs_attention:
            lines.append("❓ NEEDS YOUR ATTENTION")
            for lug in queue["needs_clarification"]:
                title = lug.get("title", lug.get("id", "Untitled"))
                lines.append(f"  🔴 {title[:52]}")
            for lug in queue["accepted"]:
                title = lug.get("title", lug.get("id", "Untitled"))
                lines.append(f"  ✅ {title[:52]}")
                lines.append("     Ready for your acceptance testing")
            lines.append("")

        if queue["in_progress"]:
            lines.append("⚡ IN PROGRESS")
            for lug in queue["in_progress"][:5]:
                title = lug.get("title", lug.get("id", "Untitled"))
                updated_at = lug.get("workflow", {}).get("updated_at")
                owner = lug.get("workflow", {}).get("current_owner", "unknown")
                age = self._age_string(updated_at) if updated_at else "unknown"
                lines.append(f"  🔵 {title[:52]}")
                lines.append(f"     {owner} ({age})")
            lines.append("")

        if queue["ready"]:
            lines.append("🆕 READY FOR WORK")
            for lug in queue["ready"][:5]:
                title = lug.get("title", lug.get("id", "Untitled"))
                impact = lug.get("impact", "?")
                lines.append(f"  ⚪ {title[:52]}")
                lines.append(f"     Impact: {impact}")
            lines.append("")
            lines.append("  💡 Builder session controls:")
            lines.append("     /wai-auto-on")
            lines.append("     /wai-auto-parallel <n>")
            lines.append("")

        total_items = sum(len(v) for v in queue.values())
        if total_items == 0:
            lines.append("All clear! No pending work. 🚀")
        lines.append("")
        lines.append("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        return "\n".join(lines)

    def _generate_auto_mode_briefing(
        self, queue: Dict[str, List[Dict[str, Any]]]
    ) -> str:
        config = self.load_runtime_config()
        lines = [
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
            "👔 OZI AUTO MODE",
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
            "",
            f"Session key: {self.session_key()}",
            f"Max parallel: {config.get('max_parallel', 1)}",
            f"Watch mode: {'on' if config.get('watch_mode', True) else 'off'} ({config.get('poll_interval_minutes', 5)} min)",
            "",
        ]

        if queue["ready"]:
            lines.append("🚀 READY TO WORK")
            for lug in queue["ready"][:8]:
                title = lug.get("title", lug.get("id", "Untitled"))
                lug_type = lug.get("type", "unknown")
                lines.append(
                    f"  • {lug.get('id', 'unknown')} [{lug_type}] {title[:48]}"
                )
            lines.append("")
        else:
            lines.append("🚀 READY TO WORK")
            lines.append("  • none")
            lines.append("")

        lines.append("🛠 CLAIMED BY THIS SESSION")
        if queue["claimed_by_me"]:
            for lug in queue["claimed_by_me"][:8]:
                title = lug.get("title", lug.get("id", "Untitled"))
                updated_at = lug.get("workflow", {}).get("updated_at")
                age = self._age_string(updated_at) if updated_at else "unknown"
                lines.append(f"  • {lug.get('id', 'unknown')} {title[:48]} ({age})")
        else:
            lines.append("  • none")
        lines.append("")

        recent_actions = self.recent_session_actions(limit=5)
        lines.append("📜 RECENT DISPATCH ACTIVITY")
        if recent_actions:
            for entry in recent_actions:
                lines.append(f"  • {entry}")
        else:
            lines.append("  • none")
        lines.append("")
        lines.append("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        return "\n".join(lines)

    def recent_session_actions(self, limit: int = 5) -> List[str]:
        if not self.changelog_file.exists():
            return []
        actions: List[str] = []
        with open(self.changelog_file, "r") as handle:
            for line in handle:
                try:
                    entry = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if entry.get("session_key") != self.session_key():
                    continue
                action = entry.get("type", "unknown")
                lug_id = entry.get("lug_id", "unknown")
                timestamp = entry.get("timestamp", "")[:16]
                actions.append(f"{timestamp} {action} {lug_id}")
        return actions[-limit:]

    def log_changelog(self, entry: Dict[str, Any]) -> None:
        if not self.changelog_file.exists():
            self.changelog_file.parent.mkdir(parents=True, exist_ok=True)
            self.changelog_file.touch()
        entry.setdefault("timestamp", datetime.now(timezone.utc).isoformat())
        entry.setdefault("session_key", self.session_key())
        with open(self.changelog_file, "a") as handle:
            handle.write(json.dumps(entry) + "\n")

    def auto_dispatch_work(self, queue: Dict[str, List[Dict[str, Any]]]) -> List[str]:
        if not self.is_auto_mode_enabled():
            return []
        config = self.load_runtime_config()
        max_parallel = int(config.get("max_parallel", 1))
        active_claims = len(queue.get("claimed_by_me", []))
        available_slots = max(0, max_parallel - active_claims)
        if available_slots == 0:
            return []

        # Import gate evaluation
        try:
            import sys as _sys
            _sys.path.insert(0, str(Path(__file__).parent / "tools"))
            from lug_utils import evaluate_execute_when, load_phases_from_state
            phases = load_phases_from_state()
        except ImportError:
            phases = []
            evaluate_execute_when = None

        dispatched: List[str] = []
        for lug in self._roi_sorted_lugs(queue.get("ready", [])):
            if len(dispatched) >= available_slots:
                break
            lug_type = lug.get("type", lug.get("_fs_type", "unknown"))
            if lug_type in self.AUTO_EXCLUDED_TYPES:
                continue
            lug_id = lug.get("id")
            if not isinstance(lug_id, str) or not lug_id:
                continue
            # Check blocked_by and execute_when gates
            if evaluate_execute_when:
                ready, reason = evaluate_execute_when(lug, phases)
                if not ready:
                    continue
            if self._dispatch_lug_to_subagent(lug_id, lug):
                dispatched.append(lug_id)
        return dispatched

    def _roi_sorted_lugs(self, lugs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Sort lugs by ROI (highest first), falling back to FIFO."""
        try:
            import sys
            sys.path.insert(0, str(Path(__file__).parent / "tools"))
            from score_backlog import score_lug
        except ImportError:
            # Fallback to FIFO if scorer unavailable
            return sorted(lugs, key=lambda l: str(
                l.get("created_at") or l.get("updated_at") or l.get("id") or ""
            ))

        def roi_key(lug: Dict[str, Any]) -> float:
            lug_type = lug.get("_fs_type", lug.get("type", "other"))
            status = lug.get("_fs_status", "open")
            return score_lug(lug, lug_type, status)

        return sorted(lugs, key=roi_key, reverse=True)

    def _dispatch_lug_to_subagent(self, lug_id: str, lug: Dict[str, Any]) -> bool:
        workflow = {
            "current_owner": self.current_owner_name(),
            "assigned_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat(),
            "dispatch_method": "auto",
            "auto_session_key": self.session_key(),
            "subagent_prompt": self._create_implementation_prompt(lug_id, lug),
        }
        updated = self._update_lug_status(lug_id, "in_progress", workflow)
        if not updated:
            return False
        print(self.render_start_summary(lug_id, lug))
        self.log_changelog(
            {
                "type": "auto_dispatch",
                "lug_id": lug_id,
                "lug_type": lug.get("type", "unknown"),
                "title": lug.get("title", lug_id),
                "dispatched_by": "ozi",
            }
        )
        return True

    def render_start_summary(self, lug_id: str, lug: Dict[str, Any]) -> str:
        title = lug.get("title", lug_id)
        lug_type = str(lug.get("type", "task")).replace("-", " ").title()
        category = lug.get("category")
        tags = lug.get("tags", [])

        if category:
            type_label = f"{lug_type} / {str(category).replace('-', ' ').title()}"
        elif "refactor" in tags and lug_type.lower() != "refactor":
            type_label = f"{lug_type} / Refactor"
        else:
            type_label = lug_type

        priority = str(lug.get("priority", "medium")).title()
        priority_label = (
            f"{priority} (Downtime work)" if "downtime-work" in tags else priority
        )
        description = str(lug.get("description", "No description provided.")).strip()
        tag_label = ", ".join(tags) if tags else "none"

        return "\n".join(
            [
                "",
                f"1. {title} (ID: {lug_id})",
                f"* Type: {type_label}",
                f"* Priority: {priority_label}",
                f"* Tags: {tag_label}",
                f"* Description: {description}",
            ]
        )

    def _create_implementation_prompt(self, lug_id: str, lug: Dict[str, Any]) -> str:
        title = lug.get("title", lug.get("t", "Untitled"))
        description = lug.get("description", lug.get("summary", "No description"))
        lug_type = lug.get("type", lug.get("_fs_type", "task"))
        file_path = lug.get("_file_path", f"WAI-Spoke/lugs/bytype/{lug_type}/open/{lug_id}.json")
        perceive = lug.get("perceive", "")
        execute = lug.get("execute", "")
        verify = lug.get("verify", "")
        pev_block = ""
        if perceive or execute or verify:
            pev_block = (
                f"\nPEV Contract:\n"
                f"  Perceive: {perceive}\n"
                f"  Execute: {execute}\n"
                f"  Verify: {verify}\n"
            )
        return (
            "You are a builder sub-agent dispatched by Ozi.\n\n"
            f"Your ONLY job: Complete {lug_type} {lug_id}\n\n"
            f"Title: {title}\n\n"
            f"Description:\n{description}\n"
            f"{pev_block}\n"
            "Instructions:\n"
            f"1. Read the full lug from: {file_path}\n"
            "2. Follow the PEV contract: perceive → execute → verify\n"
            "3. Stay in scope — only change what the lug specifies\n"
            "4. Update the lug file with progress and completion notes\n"
            "5. When complete, move lug to completed/ and set status to ready_for_recheck\n"
        )

    def _find_lug_file(self, lug_id: str) -> Path | None:
        """Find a lug file across all bytype/ folders."""
        if not self.bytype_dir.exists():
            return None
        for type_dir in self.bytype_dir.iterdir():
            if not type_dir.is_dir():
                continue
            for status_dir in type_dir.iterdir():
                if not status_dir.is_dir():
                    continue
                candidate = status_dir / f"{lug_id}.json"
                if candidate.exists():
                    return candidate
        return None

    def _update_lug_status(
        self, lug_id: str, status: str, workflow: Dict[str, Any]
    ) -> bool:
        lug_path = self._find_lug_file(lug_id)
        if not lug_path:
            return False

        try:
            lug = json.loads(lug_path.read_text())
        except (json.JSONDecodeError, OSError):
            return False

        lug["status"] = status
        lug["s"] = status
        lug["updated_at"] = datetime.now(timezone.utc).isoformat()
        current_workflow = lug.get("workflow", {})
        current_workflow.update(workflow)
        lug["workflow"] = current_workflow

        # Move file to new status folder if status changed
        current_status_dir = lug_path.parent.name
        type_dir = lug_path.parent.parent
        new_status_dir = status.replace("-", "_")

        if current_status_dir != new_status_dir:
            new_dir = type_dir / new_status_dir
            new_dir.mkdir(parents=True, exist_ok=True)
            new_path = new_dir / lug_path.name
            # Remove internal metadata before saving
            lug.pop("_file_path", None)
            lug.pop("_fs_status", None)
            lug.pop("_fs_type", None)
            new_path.write_text(json.dumps(lug, indent=2) + "\n")
            lug_path.unlink()
        else:
            lug.pop("_file_path", None)
            lug.pop("_fs_status", None)
            lug.pop("_fs_type", None)
            lug_path.write_text(json.dumps(lug, indent=2) + "\n")

        return True


def run_cycle(ozi: OziWorkQueueMonitor) -> int:
    queue = ozi.scan_work_queue()
    print(ozi.generate_briefing(queue))

    dispatched_count = 0
    if ozi.is_auto_mode_enabled():
        dispatched = ozi.auto_dispatch_work(queue)
        dispatched_count = len(dispatched)
        if dispatched:
            print("")
            print("🤖 DISPATCHED NOW")
            for lug_id in dispatched:
                print(f"  • {lug_id}")
    return dispatched_count


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--watch", action="store_true", help="poll in a loop for ready work"
    )
    args = parser.parse_args()

    ozi = OziWorkQueueMonitor()
    if not ozi.is_enabled():
        print("ℹ️  Ozi work queue monitoring is disabled")
        print("   Enable with: wai skill enable ozi-work-queue-monitor")
        return

    if args.watch:
        config = ozi.load_runtime_config()
        interval_minutes = int(config.get("poll_interval_minutes", 5))
        print(
            f"👀 Ozi watch mode active for {ozi.session_key()} ({interval_minutes} min poll)"
        )
        while True:
            run_cycle(ozi)
            time.sleep(max(1, interval_minutes) * 60)
    else:
        run_cycle(ozi)


if __name__ == "__main__":
    main()
