#!/usr/bin/env python3
"""
Ozi - Chief of Staff
Work queue monitoring and autonomous dispatch system
"""

import json
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional


class OziWorkQueueMonitor:
    """Ozi's work queue monitoring and coordination system"""

    def __init__(self, spoke_path: str = "WAI-Spoke"):
        self.spoke_path = Path(spoke_path)
        self.lugs_file = self.spoke_path / "WAI-Lugs.jsonl"
        self.changelog_file = self.spoke_path / "WAI-Changelog.jsonl"
        self.skills_file = self.spoke_path / "WAI-Skills.jsonl"

    def is_enabled(self) -> bool:
        """Check if Ozi work queue monitoring is enabled"""
        try:
            with open(self.skills_file, "r") as f:
                for line in f:
                    skill = json.loads(line)
                    if skill["id"] == "ozi-work-queue-monitor":
                        return skill.get(
                            "enabled", skill.get("enabled_by_default", False)
                        )
            return False
        except (FileNotFoundError, json.JSONDecodeError):
            return False

    def scan_work_queue(self) -> Dict[str, List[Dict]]:
        """Scan all lugs and categorize by status"""

        queue = {
            "ready": [],
            "in_progress": [],
            "ready_for_recheck": [],
            "accepted": [],
            "needs_clarification": [],
            "stale": [],
            "completed_recently": [],
        }

        if not self.lugs_file.exists():
            return queue

        now = datetime.now(timezone.utc)

        with open(self.lugs_file, "r") as f:
            for line in f:
                try:
                    lug = json.loads(line)

                    status = lug.get("status", "unknown")

                    # Ready for dispatch
                    if status == "ready":
                        queue["ready"].append(lug)

                    # In progress
                    elif status == "in_progress":
                        updated_at = lug.get("workflow", {}).get("updated_at")
                        if updated_at:
                            updated_dt = datetime.fromisoformat(
                                updated_at.replace("Z", "+00:00")
                            )
                            if (now - updated_dt) > timedelta(hours=4):
                                queue["stale"].append(lug)
                            else:
                                queue["in_progress"].append(lug)
                        else:
                            queue["in_progress"].append(lug)

                    # Ready for verification
                    elif status == "ready_for_recheck":
                        queue["ready_for_recheck"].append(lug)

                    # Accepted, needs user review
                    elif status == "accepted":
                        user_reviewed = lug.get("user_reviewed", False)
                        if not user_reviewed:
                            queue["accepted"].append(lug)

                    # Needs clarification
                    elif status == "needs_clarification":
                        queue["needs_clarification"].append(lug)

                    # Recently completed
                    elif status in ["completed", "accepted"]:
                        updated_at = lug.get("updated_at") or lug.get("completed_at")
                        if updated_at:
                            updated_dt = datetime.fromisoformat(
                                updated_at.replace("Z", "+00:00")
                            )
                            if (now - updated_dt) < timedelta(hours=24):
                                queue["completed_recently"].append(lug)

                except (json.JSONDecodeError, KeyError):
                    continue

        return queue

    def generate_briefing(self, queue: Dict[str, List[Dict]]) -> str:
        """Generate Ozi's briefing text"""

        briefing = []
        briefing.append("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        briefing.append("👔 OZI'S BRIEFING")
        briefing.append("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        briefing.append("")

        # Greeting based on time
        hour = datetime.now().hour
        if 5 <= hour < 12:
            greeting = "Good morning"
        elif 12 <= hour < 17:
            greeting = "Good afternoon"
        elif 17 <= hour < 21:
            greeting = "Good evening"
        else:
            greeting = "Hello"

        briefing.append(f"{greeting}! Here's your work queue:")
        briefing.append("")

        # Completed work
        if queue["completed_recently"]:
            briefing.append("🎉 COMPLETED (Since Last Session)")
            for lug in queue["completed_recently"][:5]:  # Show top 5
                title = lug.get("title", lug.get("id", "Untitled"))
                impact = lug.get("impact", "?")
                briefing.append(f"  ✅ {title[:60]}")
                briefing.append(f"     Impact: {impact}")
            if len(queue["completed_recently"]) > 5:
                briefing.append(
                    f"  ... and {len(queue['completed_recently']) - 5} more"
                )
            briefing.append("")

        # Needs attention
        needs_attention = queue["needs_clarification"] + queue["accepted"]
        if needs_attention:
            briefing.append("❓ NEEDS YOUR ATTENTION")

            for lug in queue["needs_clarification"]:
                title = lug.get("title", lug.get("id", "Untitled"))
                question = (
                    lug.get("workflow", {})
                    .get("clarification_question", {})
                    .get("question", "Needs input")
                )
                briefing.append(f"  🔴 {title[:50]}")
                briefing.append(f"     {question[:70]}")

            for lug in queue["accepted"]:
                title = lug.get("title", lug.get("id", "Untitled"))
                briefing.append(f"  ✅ {title[:50]}")
                briefing.append(f"     Ready for your acceptance testing")

            briefing.append("")

        # In progress
        if queue["in_progress"]:
            briefing.append("⚡ IN PROGRESS")
            for lug in queue["in_progress"][:5]:
                title = lug.get("title", lug.get("id", "Untitled"))
                owner = lug.get("workflow", {}).get("current_owner", "Unknown")
                updated = lug.get("workflow", {}).get("updated_at", "")
                if updated:
                    try:
                        updated_dt = datetime.fromisoformat(
                            updated.replace("Z", "+00:00")
                        )
                        delta = datetime.now(timezone.utc) - updated_dt
                        if delta.seconds < 3600:
                            time_str = f"{delta.seconds // 60}min ago"
                        else:
                            time_str = f"{delta.seconds // 3600}hr ago"
                    except:
                        time_str = "recently"
                else:
                    time_str = "unknown"

                briefing.append(f"  🔵 {title[:50]}")
                briefing.append(f"     {owner} (updated {time_str})")
            briefing.append("")

        # Ready for work
        if queue["ready"]:
            briefing.append("🆕 READY FOR WORK")
            for lug in queue["ready"][:3]:
                title = lug.get("title", lug.get("id", "Untitled"))
                impact = lug.get("impact", "?")
                priority = lug.get("priority", "medium")
                briefing.append(f"  ⚪ {title[:50]}")
                briefing.append(f"     Impact: {impact} | Priority: {priority}")

            if not self.is_enabled():
                briefing.append("")
                briefing.append("  💡 Enable auto-dispatch:")
                briefing.append("     $ wai skill enable ozi-work-queue-monitor")
            briefing.append("")

        # Stale work
        if queue["stale"]:
            briefing.append("⏰ STALE WORK (>4hrs no activity)")
            for lug in queue["stale"]:
                title = lug.get("title", lug.get("id", "Untitled"))
                owner = lug.get("workflow", {}).get("current_owner", "Unknown")
                briefing.append(f"  ⏸️  {title[:50]}")
                briefing.append(f"     Assigned: {owner} (needs attention)")
            briefing.append("")

        # Summary
        total_items = sum(len(v) for v in queue.values())
        if total_items == 0:
            briefing.append("All clear! No pending work. 🚀")
        else:
            briefing.append(f"Total items: {total_items}")
            briefing.append("")
            if queue["ready"] and not queue["needs_clarification"]:
                briefing.append("Everything else running smoothly! 🚀")
            elif queue["needs_clarification"]:
                briefing.append(
                    f"⚠️  {len(queue['needs_clarification'])} items need your input"
                )

        briefing.append("")
        briefing.append("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

        return "\n".join(briefing)

    def log_changelog(self, entry: Dict[str, Any]):
        """Log entry to changelog"""

        # Ensure changelog exists
        if not self.changelog_file.exists():
            self.changelog_file.parent.mkdir(parents=True, exist_ok=True)
            self.changelog_file.touch()

        # Add timestamp if not present
        if "timestamp" not in entry:
            entry["timestamp"] = datetime.now(timezone.utc).isoformat()

        # Append entry
        with open(self.changelog_file, "a") as f:
            f.write(json.dumps(entry) + "\n")


def main():
    """Run Ozi's briefing"""
    ozi = OziWorkQueueMonitor()

    if not ozi.is_enabled():
        print("ℹ️  Ozi work queue monitoring is disabled")
        print("   Enable with: wai skill enable ozi-work-queue-monitor")
        return

    queue = ozi.scan_work_queue()
    briefing = ozi.generate_briefing(queue)
    print(briefing)


if __name__ == "__main__":
    main()
