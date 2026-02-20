"""
Spoke Synthesis - Synthesize framework teachings + spoke variables into merged config.

Framework pushes generic templates, but spokes own their customizations.
On wakeup, agent reads teachings + spoke-vars and synthesizes project-specific config.

Usage:
    from wai.spoke_synthesis import synthesize_spoke_config, load_or_create_spoke_vars

    # On wakeup: synthesize teachings with spoke vars
    synthesis = synthesize_spoke_config(spoke_path)

    # Get or create spoke variables
    vars_lug = load_or_create_spoke_vars(spoke_path)
"""

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, List, Optional


def now_iso() -> str:
    """Return current UTC timestamp in ISO format."""
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def load_or_create_spoke_vars(spoke_path: Path) -> Dict[str, Any]:
    """
    Load spoke variables from lug-spoke-vars.jsonl, or create defaults from WAI-State.json.

    Args:
        spoke_path: Path to project root

    Returns:
        Spoke variables lug dict
    """
    lugs_dir = spoke_path / "WAI-Spoke" / "lugs"
    vars_file = lugs_dir / "lug-spoke-vars.jsonl"

    # Try to load existing
    if vars_file.exists():
        try:
            content = vars_file.read_text(encoding="utf-8").strip()
            if content:
                return json.loads(content)
        except (json.JSONDecodeError, IOError):
            pass

    # Create from WAI-State.json
    state_file = spoke_path / "WAI-Spoke" / "WAI-State.json"
    vars_lug = {
        "id": "lug-spoke-vars",
        "ty": "config",
        "title": "Spoke Local Variables",
        "vars": {
            "project_name": "",
            "project_description": "",
            "stack": [],
            "ai_style": "Balanced autonomy with check-ins for critical decisions",
            "custom_rules": []
        },
        "created_at": now_iso(),
        "last_modified_at": now_iso()
    }

    if state_file.exists():
        try:
            state = json.loads(state_file.read_text(encoding="utf-8"))

            # Extract project info
            wheel = state.get("wheel", {})
            foundation = state.get("_project_foundation", {})
            identity = foundation.get("identity", {})

            vars_lug["vars"]["project_name"] = (
                wheel.get("name") or
                wheel.get("abbrev") or
                ""
            )
            vars_lug["vars"]["project_description"] = (
                identity.get("one_sentence_description") or
                wheel.get("description") or
                ""
            )

            # Stack from state
            stack = state.get("stack", [])
            if stack:
                vars_lug["vars"]["stack"] = stack

            # AI interaction preference
            approach = foundation.get("approach", {})
            ai_pref = approach.get("ai_interaction_preference")
            if ai_pref:
                vars_lug["vars"]["ai_style"] = ai_pref

        except (json.JSONDecodeError, IOError):
            pass

    # Save the new vars lug
    lugs_dir.mkdir(parents=True, exist_ok=True)
    try:
        vars_file.write_text(json.dumps(vars_lug, indent=2), encoding="utf-8")
    except IOError:
        pass

    return vars_lug


def scan_teachings(ingest_path: Path) -> List[Dict[str, Any]]:
    """
    Scan pending teachings from seed/ingest/ directory.

    Args:
        ingest_path: Path to WAI-Spoke/seed/ingest/

    Returns:
        List of teaching dicts with name, type, content
    """
    teachings = []

    if not ingest_path.exists():
        return teachings

    for teaching_file in ingest_path.glob("*.teaching"):
        try:
            content = teaching_file.read_text(encoding="utf-8")
            name = teaching_file.stem  # Remove .teaching extension

            # Determine type based on filename
            if name.endswith(".md"):
                teaching_type = "markdown"
            elif name.endswith(".json"):
                teaching_type = "json"
            elif name.endswith(".jsonl"):
                teaching_type = "jsonl"
            else:
                teaching_type = "text"

            # Check if this is an IDE template (CLAUDE.md, GEMINI.md, AGENTS.md)
            is_ide_template = any(
                ide in name.upper() for ide in ["CLAUDE", "GEMINI", "AGENTS", "CURSOR"]
            )

            teachings.append({
                "name": name,
                "type": teaching_type,
                "is_ide_template": is_ide_template,
                "content": content,
                "file_path": str(teaching_file)
            })
        except IOError:
            continue

    return teachings


def apply_template_vars(content: str, vars: Dict[str, Any]) -> str:
    """
    Apply spoke variables to template content.

    Replaces placeholders like {{PROJECT_NAME}}, {{PROJECT_DESCRIPTION}}, etc.

    Args:
        content: Template content with placeholders
        vars: Spoke variables dict

    Returns:
        Content with placeholders replaced
    """
    # Define variable mappings
    replacements = {
        "{{PROJECT_NAME}}": vars.get("project_name", ""),
        "{{PROJECT_DESCRIPTION}}": vars.get("project_description", ""),
        "{{STACK}}": ", ".join(vars.get("stack", [])),
        "{{AI_STYLE}}": vars.get("ai_style", ""),
    }

    # Apply replacements
    result = content
    for placeholder, value in replacements.items():
        if value:  # Only replace if value is non-empty
            result = result.replace(placeholder, str(value))

    # Handle custom rules (as bullet list)
    custom_rules = vars.get("custom_rules", [])
    if custom_rules:
        rules_text = "\n".join(f"- {rule}" for rule in custom_rules)
        result = result.replace("{{CUSTOM_RULES}}", rules_text)
    else:
        # Remove the placeholder line entirely if no custom rules
        result = re.sub(r".*\{\{CUSTOM_RULES\}\}.*\n?", "", result)

    return result


def save_synthesis_lug(spoke_path: Path, synthesis: Dict[str, Any]) -> bool:
    """
    Save synthesis lug to spoke's lugs directory.

    Args:
        spoke_path: Path to project root
        synthesis: Synthesis dict to save

    Returns:
        True if successful
    """
    lugs_dir = spoke_path / "WAI-Spoke" / "lugs"
    synthesis_file = lugs_dir / "lug-spoke-synthesis.jsonl"

    lug = {
        "id": "lug-spoke-synthesis",
        "ty": "synthesis",
        "title": "Synthesized IDE Config",
        **synthesis
    }

    try:
        lugs_dir.mkdir(parents=True, exist_ok=True)
        synthesis_file.write_text(json.dumps(lug, indent=2), encoding="utf-8")
        return True
    except IOError:
        return False


def load_synthesis_lug(spoke_path: Path) -> Optional[Dict[str, Any]]:
    """
    Load existing synthesis lug.

    Args:
        spoke_path: Path to project root

    Returns:
        Synthesis lug dict or None
    """
    synthesis_file = spoke_path / "WAI-Spoke" / "lugs" / "lug-spoke-synthesis.jsonl"

    if not synthesis_file.exists():
        return None

    try:
        return json.loads(synthesis_file.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, IOError):
        return None


def synthesize_spoke_config(spoke_path: Path, force: bool = False) -> Dict[str, Any]:
    """
    Synthesize framework teachings + spoke vars into usable config.

    Called on wakeup after teaching verification. Creates merged config
    that respects both framework patterns and spoke-specific customizations.

    Args:
        spoke_path: Path to project root
        force: If True, re-synthesize even if synthesis exists

    Returns:
        Synthesis dict with:
        - synthesized_at: Timestamp
        - from_teachings: List of teaching names processed
        - from_vars: Reference to spoke-vars lug
        - content: Synthesized content by type
    """
    ingest_path = spoke_path / "WAI-Spoke" / "seed" / "ingest"

    # Check if we need to synthesize
    if not force:
        existing = load_synthesis_lug(spoke_path)
        if existing:
            # Check if teachings have changed
            teachings = scan_teachings(ingest_path)
            existing_teachings = set(existing.get("from_teachings", []))
            current_teachings = set(t["name"] for t in teachings)

            if existing_teachings == current_teachings:
                # No new teachings, return existing
                return existing

    # Load or create spoke variables
    vars_lug = load_or_create_spoke_vars(spoke_path)
    vars = vars_lug.get("vars", {})

    # Scan teachings
    teachings = scan_teachings(ingest_path)

    # Build synthesis
    synthesis = {
        "synthesized_at": now_iso(),
        "from_teachings": [t["name"] for t in teachings],
        "from_vars": "lug-spoke-vars",
        "content": {
            "ide_additions": {},
            "custom_wakeup_steps": [],
            "merged_rules": []
        }
    }

    # Process each teaching
    for teaching in teachings:
        if teaching["is_ide_template"]:
            # Apply vars to IDE templates
            synthesized_content = apply_template_vars(
                teaching["content"],
                vars
            )
            synthesis["content"]["ide_additions"][teaching["name"]] = synthesized_content

    # Add custom rules from vars to merged rules
    custom_rules = vars.get("custom_rules", [])
    synthesis["content"]["merged_rules"].extend(custom_rules)

    # Save synthesis
    save_synthesis_lug(spoke_path, synthesis)

    return synthesis


def update_spoke_vars(
    spoke_path: Path,
    updates: Dict[str, Any],
    append_rules: Optional[List[str]] = None
) -> bool:
    """
    Update spoke variables with new values.

    Args:
        spoke_path: Path to project root
        updates: Dict of vars to update
        append_rules: Optional list of rules to append to custom_rules

    Returns:
        True if successful
    """
    vars_lug = load_or_create_spoke_vars(spoke_path)

    # Apply updates
    for key, value in updates.items():
        if key in vars_lug["vars"]:
            vars_lug["vars"][key] = value

    # Append rules if provided
    if append_rules:
        existing_rules = vars_lug["vars"].get("custom_rules", [])
        for rule in append_rules:
            if rule not in existing_rules:
                existing_rules.append(rule)
        vars_lug["vars"]["custom_rules"] = existing_rules

    vars_lug["last_modified_at"] = now_iso()

    # Save
    lugs_dir = spoke_path / "WAI-Spoke" / "lugs"
    vars_file = lugs_dir / "lug-spoke-vars.jsonl"

    try:
        lugs_dir.mkdir(parents=True, exist_ok=True)
        vars_file.write_text(json.dumps(vars_lug, indent=2), encoding="utf-8")
        return True
    except IOError:
        return False


def get_synthesis_status(spoke_path: Path) -> Dict[str, Any]:
    """
    Get status of spoke synthesis.

    Args:
        spoke_path: Path to project root

    Returns:
        Status dict with synthesis state info
    """
    synthesis = load_synthesis_lug(spoke_path)
    vars_lug = load_or_create_spoke_vars(spoke_path)
    ingest_path = spoke_path / "WAI-Spoke" / "seed" / "ingest"
    teachings = scan_teachings(ingest_path)

    return {
        "has_synthesis": synthesis is not None,
        "synthesized_at": synthesis.get("synthesized_at") if synthesis else None,
        "teachings_count": len(teachings),
        "teachings_pending": [t["name"] for t in teachings],
        "vars_configured": bool(vars_lug.get("vars", {}).get("project_name")),
        "custom_rules_count": len(vars_lug.get("vars", {}).get("custom_rules", []))
    }


__all__ = [
    "load_or_create_spoke_vars",
    "scan_teachings",
    "apply_template_vars",
    "synthesize_spoke_config",
    "update_spoke_vars",
    "get_synthesis_status",
    "load_synthesis_lug",
]
