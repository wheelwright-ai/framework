"""
Bootstrap generator for GPT-only sessions.

Creates a minimal, single-file workflow that can be reconciled into full WAI files
on the next Closeout.
"""

from pathlib import Path
from typing import Optional

from .utils.input import print_info, print_warning, print_success


def _bootstrap_readme() -> str:
    return (
        "# WAI Bootstrap (GPT Single-File Mode)\n\n"
        "Use this folder when you are in a GPT session without the WAI CLI.\n"
        "Goal: produce ONE minimal file that captures the benefits of WAI tracking.\n\n"
        "## What WAI Is (Short)\n"
        "Wheelwright AI (WAI) keeps project context continuous across sessions.\n"
        "It stores identity, scope, decisions, and next actions so any AI can\n"
        "pick up the work with full context.\n\n"
        "## How to Use This Bootstrap\n"
        "1) Open this README and WAI-Minimal.template.md in your GPT session.\n"
        "2) Ask GPT to fill the template for your project in ONE file.\n"
        "3) Save the result as WAI-Minimal.md.\n"
        "4) After initializing Wheelwright locally, move it to:\n"
        "   WAI-Spoke/seed/ingest/WAI-Minimal.md\n"
        "5) Run WAI-CLI closeout (or Shipit). Closeout will ingest and\n"
        "   distribute the content into WAI-State.json, WAI-State.md, and WAI-Guide.md.\n\n"
        "## Notes\n"
        "- Keep the output to a single file.\n"
        "- Be concise: focus on identity, scope, decisions, and next actions.\n"
        "- Avoid secrets you would not store in the repo.\n"
    )


def _bootstrap_template() -> str:
    return (
        "# WAI Minimal Seed\n\n"
        "## Project Identity\n"
        "- Name:\n"
        "- One-liner:\n"
        "- Type (code/research/writing/design/mixed):\n"
        "- Success looks like:\n\n"
        "## Scope\n"
        "- In scope:\n"
        "- Out of scope:\n"
        "- Constraints:\n\n"
        "## Current Focus\n"
        "- Phase:\n"
        "- Goals (now):\n"
        "- Next actions (3-5):\n\n"
        "## Decisions\n"
        "- [YYYY-MM-DD] Decision / Rationale / Impact (1-10)\n\n"
        "## AI Collaboration Notes\n"
        "- Collaboration style:\n"
        "- Review expectations:\n"
        "- Preferred tools or workflow:\n"
    )


def refresh_bootstrap(framework_root: Optional[Path] = None, verbose: bool = True) -> bool:
    """Regenerate the bootstrap folder from in-code templates."""
    root = framework_root or Path(__file__).resolve().parent.parent
    bootstrap_dir = root / "bootstrap"

    try:
        bootstrap_dir.mkdir(parents=True, exist_ok=True)
        (bootstrap_dir / "README.md").write_text(_bootstrap_readme(), encoding="utf-8")
        (bootstrap_dir / "WAI-Minimal.template.md").write_text(_bootstrap_template(), encoding="utf-8")
    except Exception as exc:
        if verbose:
            print_warning(f"  Bootstrap refresh failed: {exc}")
        return False

    if verbose:
        print_success("  Bootstrap refreshed: bootstrap/README.md, bootstrap/WAI-Minimal.template.md")
    return True
