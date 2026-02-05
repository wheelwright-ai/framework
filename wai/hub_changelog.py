"""
Hub Changelog Generator

Automatically generates changelogs from lug metadata, grouped by module,
category, and contributor. Used during teach/learn cycles to communicate
what changed in each module version.
"""

import json
from pathlib import Path
from typing import Dict, Any, List, Tuple
from datetime import datetime


class HubChangelogGenerator:
    """Generates changelogs from pending lugs for hub distribution"""

    def __init__(self, spoke_dir: Path):
        self.spoke_dir = spoke_dir
        self.lugs_dir = spoke_dir / "lugs"
        self.module_versions_path = spoke_dir / "WAI-Module-Versions.json"

    def load_module_versions(self) -> Dict[str, Any]:
        """Load spoke's module adoption state"""
        if not self.module_versions_path.exists():
            return {}
        with open(self.module_versions_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def load_lug(self, lug_id: str) -> Dict[str, Any]:
        """Load a specific lug by ID from JSONL files"""
        # Search all JSONL files in lugs directory
        if self.lugs_dir.exists():
            for jsonl_file in self.lugs_dir.glob("*.jsonl"):
                with open(jsonl_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        if not line.strip():
                            continue
                        try:
                            data = json.loads(line)
                            # Check both full ID and short ID
                            if data.get('i', '').startswith(lug_id) or data.get('id', '').startswith(lug_id):
                                return data
                        except json.JSONDecodeError:
                            continue
        return {}

    def get_pending_lugs_by_module(self) -> Dict[str, List[Dict[str, Any]]]:
        """Get all pending lugs grouped by module"""
        module_versions = self.load_module_versions()
        pending_by_module = {}

        adopted_modules = module_versions.get("adopted_modules", {})
        for module_name, info in adopted_modules.items():
            if info.get("status") != "dirty":
                continue

            pending_lug_ids = info.get("pending_lugs", [])
            if not pending_lug_ids:
                continue

            lugs = []
            for lug_id in pending_lug_ids:
                lug_data = self.load_lug(lug_id[:12])  # Use short ID
                if lug_data:
                    lugs.append(lug_data)

            if lugs:
                pending_by_module[module_name] = lugs

        return pending_by_module

    def group_lugs_by_category(self, lugs: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """Group lugs by category"""
        by_category = {}
        for lug in lugs:
            category = lug.get("category", "uncategorized")
            if category not in by_category:
                by_category[category] = []
            by_category[category].append(lug)
        return by_category

    def format_lug_entry(self, lug: Dict[str, Any]) -> str:
        """Format a single lug as a changelog entry"""
        title = lug.get("t") or lug.get("title", "Untitled")
        description = lug.get("description", "")
        impact = lug.get("impact", lug.get("im", "unknown"))

        # Get subcategory if available
        subcategory = lug.get("subcategory")
        subcategory_str = f" ({subcategory})" if subcategory else ""

        # Format entry
        entry = f"- {title}{subcategory_str}"
        if description and len(description) < 100:
            entry += f": {description}"
        if impact != "unknown":
            entry += f" [impact: {impact}]"

        return entry

    def generate_module_changelog(self, module_name: str, current_version: str, new_version: str) -> Dict[str, Any]:
        """Generate changelog for a specific module"""
        pending_by_module = self.get_pending_lugs_by_module()
        lugs = pending_by_module.get(module_name, [])

        if not lugs:
            return {
                "module": module_name,
                "old_version": current_version,
                "new_version": new_version,
                "changes": {},
                "contributors": [],
                "breaking_changes": []
            }

        # Group by category
        by_category = self.group_lugs_by_category(lugs)

        # Format changes
        changes = {}
        contributors = set()
        breaking_changes = []

        for category, category_lugs in by_category.items():
            changes[category] = []
            for lug in category_lugs:
                entry = self.format_lug_entry(lug)
                changes[category].append(entry)

                # Track contributors (from session_id or extras)
                # For now, note as "wheelwright-framework"
                contributors.add("wheelwright-framework")

                # Check if breaking change
                if lug.get("hub_submission", {}).get("breaking_change"):
                    breaking_changes.append(lug.get("title", "Untitled"))

        return {
            "module": module_name,
            "old_version": current_version,
            "new_version": new_version,
            "changes": changes,
            "contributors": list(contributors),
            "breaking_changes": breaking_changes
        }

    def generate_full_changelog(self) -> Dict[str, Any]:
        """Generate full changelog for all dirty modules"""
        module_versions = self.load_module_versions()
        pending_by_module = self.get_pending_lugs_by_module()

        changelogs = []
        spoke_id = module_versions.get("spoke_id", "unknown")
        spoke_name = module_versions.get("spoke_name", "Unknown Spoke")

        for module_name, lugs in pending_by_module.items():
            module_info = module_versions.get("adopted_modules", {}).get(module_name, {})
            current_version = module_info.get("version", "unknown")
            clean_version = module_info.get("clean_version", current_version.split("-")[0])

            # Calculate new version (bump minor)
            if "." in clean_version:
                parts = clean_version.split(".")
                major = int(parts[0])
                minor = int(parts[1]) if len(parts) > 1 else 0
                new_version = f"{major}.{minor + 1}"
            else:
                new_version = clean_version

            changelog = self.generate_module_changelog(module_name, clean_version, new_version)
            if changelog["changes"]:
                changelogs.append(changelog)

        return {
            "spoke_id": spoke_id,
            "spoke_name": spoke_name,
            "timestamp": datetime.now().isoformat(),
            "modules": changelogs
        }

    def format_changelog_markdown(self, changelog_data: Dict[str, Any]) -> str:
        """Format changelog as markdown"""
        lines = []

        lines.append(f"# Changelog - {changelog_data['spoke_name']}")
        lines.append(f"**Spoke ID:** {changelog_data['spoke_id']}")
        lines.append(f"**Generated:** {changelog_data['timestamp']}")
        lines.append("")

        for module_changelog in changelog_data["modules"]:
            module = module_changelog["module"]
            old_ver = module_changelog["old_version"]
            new_ver = module_changelog["new_version"]

            lines.append(f"## {module} ({old_ver} → {new_ver})")
            lines.append("")

            # Breaking changes first
            if module_changelog["breaking_changes"]:
                lines.append("### ⚠️ Breaking Changes")
                for change in module_changelog["breaking_changes"]:
                    lines.append(f"- {change}")
                lines.append("")

            # Changes by category
            for category, entries in module_changelog["changes"].items():
                category_title = category.replace("_", " ").title()
                lines.append(f"### {category_title}")
                for entry in entries:
                    lines.append(entry)
                lines.append("")

            # Contributors
            if module_changelog["contributors"]:
                contributors_str = ", ".join(module_changelog["contributors"])
                lines.append(f"**Contributors:** {contributors_str}")
                lines.append("")

            lines.append("---")
            lines.append("")

        return "\n".join(lines)

    def save_changelog(self, changelog_data: Dict[str, Any], output_path: Path):
        """Save changelog to file"""
        markdown = self.format_changelog_markdown(changelog_data)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(markdown)


def cmd_generate_changelog(spoke_dir: Path):
    """CLI command to generate changelog from pending lugs"""
    generator = HubChangelogGenerator(spoke_dir)

    changelog = generator.generate_full_changelog()

    if not changelog["modules"]:
        print("✅ No pending changes - all modules clean!")
        print("   Nothing to generate changelog from.")
        return

    print(f"\n{'=' * 60}")
    print(f"Generated Changelog - {changelog['spoke_name']}")
    print(f"{'=' * 60}")
    print()

    markdown = generator.format_changelog_markdown(changelog)
    print(markdown)

    # Offer to save
    output_path = spoke_dir / "CHANGELOG-PENDING.md"
    print(f"\n💾 Save to {output_path}? (y/n): ", end="", flush=True)
    try:
        response = input().strip().lower()
        if response == 'y':
            generator.save_changelog(changelog, output_path)
            print(f"✅ Saved to {output_path}")
        else:
            print("❌ Not saved")
    except EOFError:
        # Non-interactive mode, auto-save
        generator.save_changelog(changelog, output_path)
        print(f"\n✅ Auto-saved to {output_path}")


if __name__ == "__main__":
    import sys
    spoke_dir = Path(sys.argv[1]) if len(sys.argv) > 1 else Path.cwd() / "WAI-Spoke"
    cmd_generate_changelog(spoke_dir)
