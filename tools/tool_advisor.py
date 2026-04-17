#!/usr/bin/env python3
"""
tool_advisor.py — Cross-tool configuration audit and safe auto-remediation.

This advisor unifies Claude, Gemini, and Codex/OpenAI configuration health.
It is designed to be cheap in "mark stale" mode for hooks, and more thorough
for explicit or Ozi-driven audit passes.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import re
import shutil
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path


ADVISOR_VERSION = "1.0.0"
FRAMEWORK_ROOT = Path(__file__).resolve().parent.parent
WATCH_PATHS = [
    "AGENTS.md",
    "CLAUDE.md",
    "GEMINI.md",
    ".claude/settings.json",
    ".gemini/settings.json",
    ".geminiignore",
    "WAI-Spoke/commands/wai.md",
    "WAI-Spoke/skills/wai/wai.md",
    "templates/commands/wai.md",
    "templates/spoke/skills/wai/wai.md",
    "templates/spoke/GEMINI.md",
    "templates/gemini/GEMINI.md",
    "templates/spoke/AGENTS.md",
    "templates/codex/AGENTS.md",
    "templates/spoke/.claude/settings.json",
    "templates/claude/settings.json",
    "bootstrap/spoke-upgrade.sh",
]
SCHEDULE_INDEX_PATH = Path("WAI-Spoke/advisors/schedule-index.json")
SAFE_GEMINI_SETTINGS = {
    "general": {"checkpointing": {"enabled": True}},
    "model": {
        "compressionThreshold": 0.4,
        "summarizeToolOutput": {
            "run_shell_command": {"tokenBudget": 1200},
        },
    },
    "context": {
        "fileName": ["GEMINI.md", "AGENTS.md"],
        "includeDirectoryTree": False,
        "discoveryMaxDirs": 64,
        "fileFiltering": {
            "respectGitIgnore": True,
            "respectGeminiIgnore": True,
            "enableRecursiveFileSearch": True,
        },
    },
}
SAFE_GEMINI_IGNORE_PATTERNS = [
    "WAI-Spoke/sessions/",
    "WAI-Spoke/seed/",
    "WAI-Spoke/archive/",
    "WAI-Spoke/model-usage/",
    "WAI-Spoke/runtime/",
    "WAI-Spoke/WAI-LugIndex.jsonl",
    "WAI-Spoke/WAI-Lugs-archived.jsonl",
    "WAI-Spoke/WAI-State-extended.json",
    "docs/llm-full.txt",
]
GEMINI_LOOP_GUARD_LINES = [
    "Treat this `GEMINI.md` read as already satisfying the wakeup integration-file step.",
    "Do not re-read `GEMINI.md` or rescan parent `GEMINI.md` files during wakeup unless the user explicitly asks.",
]
DEAD_WAI_GUIDE_PATTERNS = [
    (
        "Read `WAI-Spoke/WAI-Guide.md` for the skill index and command map.",
        "If you need WAI command semantics, read `WAI-Spoke/commands/wai.md` or `WAI-Spoke/skills/wai/wai.md`.",
    ),
    (
        "read `WAI-Spoke/WAI-Guide.md`",
        "read `WAI-Spoke/commands/wai.md` or `WAI-Spoke/skills/wai/wai.md`",
    ),
    (
        "WAI-Spoke/WAI-Guide.md",
        "WAI-Spoke/commands/wai.md",
    ),
]
ENV_HOOK_VARS = [
    "$CLAUDE_PROJECT_DIR",
    "${CLAUDE_PROJECT_DIR}",
    "$WAI_PROJECT_DIR",
    "${WAI_PROJECT_DIR}",
    "$CODEX_PROJECT_DIR",
    "${CODEX_PROJECT_DIR}",
]

# Shared check categories — 6 dimensions scored across all tool adapters.
CATEGORY_MAP: dict[str, str] = {
    # entrypoint-quality: integration files present and functional
    "claude-md-missing": "entrypoint-quality",
    "gemini-md-missing": "entrypoint-quality",
    "wrapper-script-missing": "entrypoint-quality",
    "wrapper-script-not-executable": "entrypoint-quality",
    # context-thrift: configuration keeps context lean and non-recursive
    "gemini-loop-guard-missing": "context-thrift",
    "wakeup-guard-missing": "context-thrift",
    # stale-path-hygiene: dead refs, unresolved vars, broken hook paths
    "claude-settings-invalid": "stale-path-hygiene",
    "claude-hook-env-vars": "stale-path-hygiene",
    "claude-hook-script-missing": "stale-path-hygiene",
    "codex-dead-wai-guide": "stale-path-hygiene",
    "bootstrap-hook-env-var": "stale-path-hygiene",
    # official-source-coverage: entrypoints reference current canonical paths
    # (populated by future official-source checks)
    # template-live-parity: spoke files consistent with framework templates
    # (populated by future parity checks)
    # compatibility-redirects: legacy commands redirect to current advisor
    "maximizer-not-redirected": "compatibility-redirects",
}

# Remediation matrix — explicit classification of what the advisor will and won't auto-apply.
# "safe_auto"     : idempotent, low-risk, proven — applied automatically by default.
# "proposal_only" : correct improvement but requires human review before applying.
# "never_auto"    : high-risk; only surfaced as a finding, never modified by the advisor.
REMEDIATION_MATRIX: dict[str, list[str]] = {
    "safe_auto": [
        "claude-md-missing",  # create CLAUDE.md from framework template
        "claude-commands-missing",  # install WAI skill commands to .claude/commands/
        "claude-hook-env-vars",  # rewrite concrete paths in hook commands
        "claude-hook-script-missing",  # restore hook script from framework template
        "gemini-loop-guard-missing",  # add loop prevention block to GEMINI.md
        "wakeup-guard-missing",  # add integration-file guard to wai.md
        "wrapper-script-missing",  # install wai-enter/wai-exit from template
        "wrapper-script-not-executable",  # chmod +x on existing wrapper
        "codex-dead-wai-guide",  # remove stale WAI-Guide.md references
        "gemini-settings-missing-keys",  # merge safe Gemini settings keys
        "gemini-ignore-missing-patterns",  # extend .geminiignore with known noise paths
    ],
    "proposal_only": [
        "gemini-coverage-absent",  # suggest GEMINI.md when only AGENTS.md present
        "codex-coverage-absent",  # suggest AGENTS.md when only GEMINI.md present
        "maximizer-not-redirected",  # update legacy maximizer skills (if found)
    ],
    "never_auto": [
        "permissions-expansion",  # broadening tool allowlists
        "hook-command-rewrite",  # changing what a hook executes
        "model-selection-change",  # modifying model config values
        "permission-prompt-allowlist",  # adding items to permission allow rules
    ],
}

MAXIMIZER_REDIRECT_PATHS = [
    "templates/commands/wai-claude-maximizer.md",
    "templates/commands/wai-tool-maximizer-gemini.md",
    "WAI-Spoke/commands/wai-claude-maximizer.md",
    "WAI-Spoke/commands/wai-tool-maximizer-gemini.md",
]
CONVERGENCE_MARKERS = [
    "Finish the WAI Point briefing before",
    "Do NOT read full teaching bodies unless the user explicitly asks",
]
WAKEUP_OUTPUT_MARKERS = [
    "output the completed wai point briefing",
    "numbered next-steps plan",
]
HOOK_TEMPLATE_MAP = {
    ".claude/hooks/pre-tool-guard.sh": FRAMEWORK_ROOT
    / "templates"
    / "spoke"
    / ".claude"
    / "hooks"
    / "pre-tool-guard.sh",
    ".claude/hooks/user-prompt-submit.sh": FRAMEWORK_ROOT
    / "templates"
    / "spoke"
    / ".claude"
    / "hooks"
    / "user-prompt-submit.sh",
    ".claude/hooks/pre-compact.sh": FRAMEWORK_ROOT
    / "templates"
    / "spoke"
    / ".claude"
    / "hooks"
    / "pre-compact.sh",
    ".claude/hooks/stop-test-runner.sh": FRAMEWORK_ROOT
    / "templates"
    / "spoke"
    / ".claude"
    / "hooks"
    / "stop-test-runner.sh",
    ".claude/hooks/session-start.sh": FRAMEWORK_ROOT
    / "templates"
    / "spoke"
    / ".claude"
    / "hooks"
    / "session-start.sh",
    "WAI-Spoke/hooks/session-start.sh": FRAMEWORK_ROOT
    / "templates"
    / "spoke"
    / "hooks"
    / "session-start.sh",
}


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def read_text(path: Path) -> str:
    return path.read_text() if path.exists() else ""


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content)


def load_json(path: Path, default: dict | list | None = None):
    if not path.exists():
        return copy.deepcopy(default)
    try:
        return json.loads(path.read_text())
    except json.JSONDecodeError:
        return copy.deepcopy(default)


def write_json(path: Path, data: dict | list) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=False) + "\n")


def append_jsonl(path: Path, item: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a") as handle:
        handle.write(json.dumps(item) + "\n")


def _tag_category(findings: list[dict]) -> list[dict]:
    """Add 'category' field to each finding using CATEGORY_MAP."""
    return [
        {**f, "category": CATEGORY_MAP.get(f.get("code", ""), "uncategorized")}
        for f in findings
    ]


def _write_proposal_report(advisor_dir: Path, proposals: list[dict], ts: str) -> None:
    """Write a human-readable proposal report when actionable proposals exist."""
    if not proposals:
        return
    report = {
        "generated_at": ts,
        "count": len(proposals),
        "note": "These proposals require human review before applying. None are auto-applied.",
        "proposals": [
            {
                "code": p.get("code", "unknown"),
                "area": p.get("area", "Unknown"),
                "message": p.get("message", ""),
                "target_file": p.get("target_file"),
                "risk": p.get("risk", "low"),
                "requires_human_review": p.get("requires_human_review", True),
            }
            for p in proposals
        ],
    }
    write_json(advisor_dir / "reports" / "proposals-latest.json", report)


def _append_vector(
    advisor_dir: Path,
    state: dict,
    session_id: str | None,
    score_delta: int,
    all_findings: list[dict],
) -> None:
    """Record a per-tool score vector for trend tracking."""
    from collections import Counter

    cat_counts: Counter = Counter(
        f.get("category", "uncategorized") for f in all_findings
    )
    record = {
        "id": f"vector-{datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S')}",
        "ts": state.get("last_audit_at"),
        "session": session_id,
        "score": state.get("current_score"),
        "score_by_area": state.get("score_by_area", {}),
        "score_delta": score_delta,
        "finding_counts_by_category": {
            cat: cat_counts.get(cat, 0)
            for cat in [
                "entrypoint-quality",
                "context-thrift",
                "stale-path-hygiene",
                "official-source-coverage",
                "template-live-parity",
                "compatibility-redirects",
            ]
        },
    }
    append_jsonl(advisor_dir / "vectors.jsonl", record)


def update_schedule_index(project_root: Path, audit_ts: str) -> None:
    schedule_path = project_root / SCHEDULE_INDEX_PATH
    if not schedule_path.exists():
        return
    data = load_json(schedule_path, [])
    if not isinstance(data, list):
        return
    changed = False
    for entry in data:
        if entry.get("advisor_id") == "tool-advisor":
            entry["last_run_at"] = audit_ts
            changed = True
            break
    if changed:
        write_json(schedule_path, data)


def default_scan_state() -> dict:
    return {
        "advisor_id": "tool-advisor",
        "advisor_name": "Cross-Tool Configuration Advisor",
        "version": ADVISOR_VERSION,
        "mission_statement": (
            "Keep Claude, Gemini, and Codex/OpenAI integrations lean, "
            "non-recursive, and safe across spokes"
        ),
        "last_audit_at": None,
        "last_audit_session": None,
        "last_observed_session": None,
        "sessions_since_last_audit": 0,
        "audit_pending": True,
        "audit_reason": "never audited",
        "last_drift_at": None,
        "total_audits": 0,
        "auto_applied_count": 0,
        "current_score": 0,
        "score_by_area": {
            "Claude": None,
            "Gemini": None,
            "Codex": None,
            "Shared": None,
        },
        "pending_proposals": [],
        "last_findings": [],
        "last_fingerprint": "",
        "fingerprint_entries": {},
    }


def ensure_advisor_layout(project_root: Path, create: bool = True) -> tuple[Path, dict]:
    advisor_dir = project_root / "WAI-Spoke" / "advisors" / "tool-advisor"
    if create:
        advisor_dir.mkdir(parents=True, exist_ok=True)
        for subdir in ("reports",):
            (advisor_dir / subdir).mkdir(parents=True, exist_ok=True)
        for empty_file in ("passes.jsonl", "vectors.jsonl", "runs.jsonl"):
            target = advisor_dir / empty_file
            if not target.exists():
                target.write_text("")

    state_path = advisor_dir / "scan_state.json"
    state = load_json(state_path, default_scan_state())
    changed = False
    for key, value in default_scan_state().items():
        if key not in state:
            state[key] = copy.deepcopy(value)
            changed = True
    if state.get("version") != ADVISOR_VERSION:
        state["version"] = ADVISOR_VERSION
        changed = True
    if create and (changed or not state_path.exists()):
        write_json(state_path, state)
    return advisor_dir, state


def deep_merge(base: dict, updates: dict) -> dict:
    merged = copy.deepcopy(base)
    for key, value in updates.items():
        if isinstance(value, dict) and isinstance(merged.get(key), dict):
            merged[key] = deep_merge(merged[key], value)
        else:
            merged[key] = copy.deepcopy(value)
    return merged


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def digest_path(path: Path) -> str:
    if not path.exists():
        return "missing"
    if path.is_dir():
        parts = []
        for child in sorted(p for p in path.rglob("*") if p.is_file()):
            rel = child.relative_to(path).as_posix()
            stat = child.stat()
            parts.append(f"{rel}:{stat.st_size}:{int(stat.st_mtime)}")
        return sha256_text("\n".join(parts))
    return hashlib.sha256(path.read_bytes()).hexdigest()


def collect_fingerprint(project_root: Path) -> tuple[str, dict[str, str]]:
    entries: dict[str, str] = {}
    for rel in WATCH_PATHS:
        entries[rel] = digest_path(project_root / rel)
    payload = json.dumps(entries, sort_keys=True)
    return sha256_text(payload), entries


def parse_ts(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt


def normalize_with_trailing_newline(content: str) -> str:
    return content.rstrip() + "\n"


def ensure_gemini_loop_guard(content: str) -> tuple[str, bool]:
    lower = content.lower()
    if (
        "do not re-read `gemini.md`" in lower
        and "already satisfying" in lower
        and "integration" in lower
    ):
        return content, False

    loop_block = (
        "\n## Loop Prevention\n\n"
        f"- {GEMINI_LOOP_GUARD_LINES[0]}\n"
        f"- {GEMINI_LOOP_GUARD_LINES[1]}\n"
    )
    new_content = normalize_with_trailing_newline(content.rstrip() + loop_block)
    return new_content, True


def ensure_wakeup_guard(content: str) -> tuple[str, bool]:
    lower = content.lower()
    if "do not reopen the same integration file during wakeup" in lower:
        return content, False
    if "do not reopen the same file again during wakeup" in lower:
        return content, False

    replacements = [
        (
            "If wakeup was started from one of those integration files, treat that initial read as satisfying this step. Continue with the custom-file scan below.",
            "If wakeup was started from one of those integration files, treat that initial read as satisfying this step. Do NOT reopen the same integration file during wakeup. Continue with the custom-file scan below.",
        ),
        (
            "- Read it fully before proceeding\n- Apply any tool-specific wakeup directives (hook behavior, command aliases, etc.)\n- Note any tool-specific constraints (e.g., complexity gate, session tracking path)\n",
            "- Read it fully before proceeding\n- Apply any tool-specific wakeup directives (hook behavior, command aliases, etc.)\n- Note any tool-specific constraints (e.g., complexity gate, session tracking path)\n- If wakeup was started from that integration file, treat the initial read as already complete and do NOT reopen the same file again during wakeup\n",
        ),
    ]
    for old, new in replacements:
        if old in content:
            return content.replace(old, new), True

    step_markers = [
        "## Step 1: Load Integration File",
        "## Step 0a: Check Integration File (Tool-Specific Instructions)",
    ]
    guard_line = (
        "\nIf wakeup was started from one of those integration files, treat that initial read "
        "as satisfying this step. Do NOT reopen the same integration file during wakeup.\n"
    )
    for marker in step_markers:
        if marker in content:
            return content.replace(marker, marker + guard_line, 1), True
    return content, False


def ensure_convergence_block(content: str) -> tuple[str, bool]:
    lower = content.lower()
    if (
        "finish the wai point briefing before" in lower
        and "do not read full teaching bodies unless the user explicitly asks" in lower
    ):
        return content, False

    anchor = "## Step 5: Discover Teachings"
    block = (
        "\nConvergence rules for all tools:\n"
        "- Finish the WAI Point briefing before pausing for teaching approval or any other side action.\n"
        "- During wakeup, inspect teachings using filenames and lightweight header/frontmatter fields only. Do NOT read full teaching bodies unless the user explicitly asks to review them now.\n"
        '- If pending teachings exist, include them in the briefing under a compact "Pending Teachings" section, then ask what to do next.\n'
    )
    if anchor in content:
        return content.replace(anchor, anchor + block, 1), True
    return normalize_with_trailing_newline(content.rstrip() + "\n\n" + block), True


def ensure_brief_first_section(
    content: str, heading: str = "## Wakeup Convergence"
) -> tuple[str, bool]:
    lower = content.lower()
    if (
        "finish the wai point briefing before" in lower
        and "do not read full teaching bodies during wakeup" in lower
    ):
        return content, False

    block = (
        f"\n{heading}\n\n"
        "- Finish the WAI Point briefing before asking for approval on teachings or side actions.\n"
        "- During wakeup, summarize teachings from filenames/frontmatter only.\n"
        "- Do not read full teaching bodies during wakeup unless the user explicitly asks to review them now.\n"
    )
    return normalize_with_trailing_newline(content.rstrip() + block), True


def ensure_codex_output_section(content: str) -> tuple[str, bool]:
    lower = content.lower()
    if (
        "completed wai point briefing itself" in lower
        and "numbered next-steps plan" in lower
    ):
        return content, False

    block = (
        "\n## Codex Wakeup Output\n\n"
        "- During `/wai`, return the completed WAI Point briefing itself, not a transcript of the checks you ran.\n"
        "- Do not narrate shell probes, file reads, or step-by-step bootstrap work in the wakeup reply.\n"
        "- After the briefing, use one short readiness line such as `Wake complete. Ready to work.`\n"
        "- Do not append a numbered next-steps plan unless the user explicitly asks for planning.\n"
        "- If review or approval items are pending, keep them inside the briefing under `Pending Items` rather than stopping early.\n"
    )
    return normalize_with_trailing_newline(content.rstrip() + block), True


def ensure_wakeup_output_contract(content: str) -> tuple[str, bool]:
    lower = content.lower()
    if (
        "output the completed wai point briefing directly" in lower
        and "numbered next-steps plan" in lower
    ):
        return content, False

    anchor = "## Step 7: Display Briefing"
    block = (
        "\nOutput contract for all tools:\n"
        "- Output the completed WAI Point briefing directly; do not narrate shell probes or bootstrap steps before it.\n"
        "- Keep the post-brief closeout to one short readiness line such as `Wake complete. Ready to work.`\n"
        "- Do not replace the briefing with a numbered next-steps plan unless the user explicitly asks for planning.\n"
        "- If teachings or stale-task decisions need approval, list them compactly under `Pending Items` inside the briefing rather than stopping early.\n"
    )
    if anchor in content:
        return content.replace(anchor, anchor + block, 1), True
    return normalize_with_trailing_newline(content.rstrip() + "\n\n" + block), True


def ensure_gemini_settings(
    project_root: Path, apply_changes: bool = True
) -> tuple[list[dict], list[dict]]:
    settings_path = project_root / ".gemini" / "settings.json"
    before = load_json(settings_path, {})
    after = deep_merge(before, SAFE_GEMINI_SETTINGS)
    if before != after:
        if apply_changes:
            write_json(settings_path, after)
        return [
            {
                "path": str(settings_path.relative_to(project_root)),
                "action": "updated Gemini settings",
            }
        ], []
    return [], []


def ensure_gemini_ignore(
    project_root: Path, apply_changes: bool = True
) -> tuple[list[dict], list[dict]]:
    ignore_path = project_root / ".geminiignore"
    lines = ignore_path.read_text().splitlines() if ignore_path.exists() else []
    existing = {line.strip() for line in lines if line.strip()}
    missing = [
        pattern for pattern in SAFE_GEMINI_IGNORE_PATTERNS if pattern not in existing
    ]
    if not missing:
        return [], []
    updated = lines[:]
    if updated and updated[-1].strip():
        updated.append("")
    updated.extend(missing)
    if apply_changes:
        write_text(ignore_path, "\n".join(updated).rstrip() + "\n")
    return [
        {
            "path": str(ignore_path.relative_to(project_root)),
            "action": "extended .geminiignore",
        }
    ], []


def ensure_gemini_md(
    project_root: Path, apply_changes: bool = True
) -> tuple[list[dict], list[dict], list[dict]]:
    gemini_path = project_root / "GEMINI.md"
    findings: list[dict] = []
    fixes: list[dict] = []
    proposals: list[dict] = []
    if not gemini_path.exists():
        findings.append(
            {
                "area": "Gemini",
                "level": "warn",
                "code": "gemini-md-missing",
                "message": "GEMINI.md missing",
            }
        )
        return findings, fixes, proposals

    content = read_text(gemini_path)
    new_content, changed = ensure_gemini_loop_guard(content)
    if changed:
        if apply_changes:
            write_text(gemini_path, new_content)
        fixes.append(
            {"path": "GEMINI.md", "action": "added Gemini loop-prevention guard"}
        )
    lower = (new_content if changed else content).lower()
    if not changed and not (
        "do not re-read `gemini.md`" in lower
        and "already satisfying" in lower
        and "integration" in lower
    ):
        findings.append(
            {
                "area": "Gemini",
                "level": "fail",
                "code": "gemini-loop-guard-missing",
                "message": "GEMINI.md lacks wakeup loop prevention",
            }
        )
    return findings, fixes, proposals


def ensure_wakeup_files(
    project_root: Path, apply_changes: bool = True
) -> tuple[list[dict], list[dict], list[dict]]:
    findings: list[dict] = []
    fixes: list[dict] = []
    proposals: list[dict] = []
    candidates = [
        project_root / "WAI-Spoke" / "commands" / "wai.md",
        project_root / "WAI-Spoke" / "skills" / "wai" / "wai.md",
        project_root / "templates" / "commands" / "wai.md",
        project_root / "templates" / "spoke" / "skills" / "wai" / "wai.md",
    ]
    changed_any = False
    existing_any = False
    for path in candidates:
        if not path.exists():
            continue
        existing_any = True
        content = read_text(path)
        new_content, changed = ensure_wakeup_guard(content)
        new_content2, changed2 = ensure_convergence_block(new_content)
        new_content3, changed3 = ensure_wakeup_output_contract(new_content2)
        changed = changed or changed2 or changed3
        new_content = new_content3
        if changed:
            if apply_changes:
                write_text(path, new_content)
            fixes.append(
                {
                    "path": str(path.relative_to(project_root)),
                    "action": "normalized wakeup convergence guidance",
                }
            )
            changed_any = True
    if existing_any and not changed_any:
        for path in candidates:
            if not path.exists():
                continue
            lower = read_text(path).lower()
            if (
                "integration file" in lower
                and "do not reopen the same integration file during wakeup" not in lower
                and "do not reopen the same file again during wakeup" not in lower
            ):
                findings.append(
                    {
                        "area": "Gemini",
                        "level": "fail",
                        "code": "wakeup-guard-missing",
                        "message": f"{path.relative_to(project_root)} lacks integration-file loop guard",
                    }
                )
                break
    return findings, fixes, proposals


def fix_settings_hook_paths(
    project_root: Path, settings_path: Path, apply_changes: bool = True
) -> tuple[list[dict], list[dict]]:
    findings: list[dict] = []
    fixes: list[dict] = []
    data = load_json(settings_path, None)
    if not isinstance(data, dict):
        findings.append(
            {
                "area": "Claude",
                "level": "fail",
                "code": "claude-settings-invalid",
                "message": f"{settings_path.relative_to(project_root)} is invalid JSON",
            }
        )
        return findings, fixes

    changed = False
    hooks = data.get("hooks", {})
    for entries in hooks.values():
        if not isinstance(entries, list):
            continue
        for entry in entries:
            for hook in entry.get("hooks", []):
                command = hook.get("command")
                if not isinstance(command, str):
                    continue
                new_command = command
                for token in ENV_HOOK_VARS:
                    if token in new_command:
                        new_command = new_command.replace(token, str(project_root))
                if new_command != command:
                    hook["command"] = new_command
                    changed = True
    if changed:
        if apply_changes:
            write_json(settings_path, data)
        fixes.append(
            {
                "path": str(settings_path.relative_to(project_root)),
                "action": "rewrote hook commands to concrete project paths",
            }
        )

    raw = read_text(settings_path)
    if any(token in raw for token in ENV_HOOK_VARS):
        findings.append(
            {
                "area": "Claude",
                "level": "fail",
                "code": "claude-hook-env-vars",
                "message": f"{settings_path.relative_to(project_root)} still contains unresolved hook env vars",
            }
        )
    return findings, fixes


def ensure_hook_scripts(
    project_root: Path, settings_path: Path, apply_changes: bool = True
) -> tuple[list[dict], list[dict]]:
    findings: list[dict] = []
    fixes: list[dict] = []
    data = load_json(settings_path, None)
    if not isinstance(data, dict):
        return findings, fixes

    hooks = data.get("hooks", {})
    for entries in hooks.values():
        if not isinstance(entries, list):
            continue
        for entry in entries:
            for hook in entry.get("hooks", []):
                command = hook.get("command")
                if not isinstance(command, str):
                    continue
                command_path = Path(command)
                if not command_path.is_absolute():
                    command_path = (project_root / command).resolve()
                if command_path.exists():
                    continue
                try:
                    rel = command_path.relative_to(project_root).as_posix()
                except ValueError:
                    continue
                template = HOOK_TEMPLATE_MAP.get(rel)
                if template and template.exists():
                    if apply_changes:
                        write_text(command_path, template.read_text())
                        command_path.chmod(0o755)
                    fixes.append(
                        {
                            "path": rel,
                            "action": "restored missing hook script from framework template",
                        }
                    )
                else:
                    findings.append(
                        {
                            "area": "Claude",
                            "level": "warn",
                            "code": "claude-hook-script-missing",
                            "message": f"Referenced hook script missing: {rel}",
                        }
                    )
    return findings, fixes


# v1 hook paths that contain the unsafe .context.next_actions pattern
_V1_HOOK_PATHS = [
    "WAI-Spoke/_hooks/session-start.sh",
]
_V1_JQ_UNSAFE = ".context.next_actions"
_V1_JQ_SAFE = "(.context.next_actions // [])"


def check_v1_hook_null_guards(
    project_root: Path, apply_changes: bool = True
) -> tuple[list[dict], list[dict]]:
    """Detect and fix missing // [] null guard on .context.next_actions in v1 session-start hooks."""
    findings: list[dict] = []
    fixes: list[dict] = []
    for rel in _V1_HOOK_PATHS:
        hook_path = project_root / rel
        if not hook_path.exists():
            continue
        content = read_text(hook_path)
        if _V1_JQ_UNSAFE in content and _V1_JQ_SAFE not in content:
            if apply_changes:
                updated = content.replace(_V1_JQ_UNSAFE, _V1_JQ_SAFE)
                write_text(hook_path, updated)
                fixes.append(
                    {
                        "path": rel,
                        "action": "added // [] null guard to .context.next_actions jq expression",
                    }
                )
            else:
                findings.append(
                    {
                        "area": "Claude",
                        "level": "warn",
                        "code": "v1-hook-jq-null-guard",
                        "message": f"{rel}: .context.next_actions missing // [] null guard — crashes when field is null",
                    }
                )
    return findings, fixes


def ensure_agents_thrift(
    project_root: Path, agents_path: Path, apply_changes: bool = True
) -> tuple[list[dict], list[dict], list[dict]]:
    findings: list[dict] = []
    fixes: list[dict] = []
    proposals: list[dict] = []
    if not agents_path.exists():
        return findings, fixes, proposals
    content = read_text(agents_path)
    updated = content
    for old, new in DEAD_WAI_GUIDE_PATTERNS:
        updated = updated.replace(old, new)
    updated, convergence_changed = ensure_brief_first_section(updated)
    updated, codex_changed = ensure_codex_output_section(updated)
    if updated != content:
        if apply_changes:
            write_text(agents_path, updated)
        fixes.append(
            {
                "path": str(agents_path.relative_to(project_root)),
                "action": "normalized AGENTS wakeup guidance",
            }
        )
    lower = read_text(agents_path).lower()
    if "wai-guide.md" in lower:
        findings.append(
            {
                "area": "Codex",
                "level": "fail",
                "code": "codex-dead-wai-guide",
                "message": f"{agents_path.relative_to(project_root)} still references WAI-Guide.md",
            }
        )
    return findings, fixes, proposals


def ensure_gemini_convergence(
    project_root: Path, path: Path, apply_changes: bool = True
) -> tuple[list[dict], list[dict], list[dict]]:
    findings: list[dict] = []
    fixes: list[dict] = []
    proposals: list[dict] = []
    if not path.exists():
        return findings, fixes, proposals
    content = read_text(path)
    updated, changed = ensure_brief_first_section(content)
    if changed:
        if apply_changes:
            write_text(path, updated)
        fixes.append(
            {
                "path": str(path.relative_to(project_root)),
                "action": "normalized Gemini wakeup guidance",
            }
        )
    return findings, fixes, proposals


def ensure_claude_convergence(
    project_root: Path, path: Path, apply_changes: bool = True
) -> tuple[list[dict], list[dict], list[dict]]:
    findings: list[dict] = []
    fixes: list[dict] = []
    proposals: list[dict] = []
    if not path.exists():
        return findings, fixes, proposals
    content = read_text(path)
    updated, changed = ensure_brief_first_section(content)
    if changed:
        if apply_changes:
            write_text(path, updated)
        fixes.append(
            {
                "path": str(path.relative_to(project_root)),
                "action": "normalized Claude wakeup guidance",
            }
        )
    return findings, fixes, proposals


def ensure_claude_commands(
    project_root: Path, apply_changes: bool = True
) -> tuple[list[dict], list[dict]]:
    """Install WAI skill command files to .claude/commands/ if the sentinel wai.md is missing."""
    findings: list[dict] = []
    fixes: list[dict] = []
    commands_dir = project_root / ".claude" / "commands"
    sentinel = commands_dir / "wai.md"
    if sentinel.exists():
        return findings, fixes
    templates_dir = FRAMEWORK_ROOT / "templates" / "commands"
    if not templates_dir.is_dir():
        findings.append(
            {
                "area": "Claude",
                "level": "warn",
                "code": "claude-commands-missing",
                "message": ".claude/commands/wai.md missing — template source not found",
            }
        )
        return findings, fixes
    if apply_changes:
        commands_dir.mkdir(parents=True, exist_ok=True)
        installed = []
        for src in sorted(templates_dir.glob("*.md")):
            dest = commands_dir / src.name
            if not dest.exists():
                shutil.copy2(src, dest)
                installed.append(src.name)
        if installed:
            fixes.append(
                {
                    "path": ".claude/commands/",
                    "action": f"installed {len(installed)} WAI skill commands from framework template",
                }
            )
    else:
        fixes.append(
            {
                "path": ".claude/commands/",
                "action": "install WAI skill commands from framework template",
            }
        )
    return findings, fixes


def audit_claude(
    project_root: Path, apply_changes: bool = True
) -> tuple[str, list[dict], list[dict], list[dict]]:
    findings: list[dict] = []
    fixes: list[dict] = []
    proposals: list[dict] = []
    settings_candidates = [
        project_root / ".claude" / "settings.json",
        project_root / "templates" / "spoke" / ".claude" / "settings.json",
        project_root / "templates" / "claude" / "settings.json",
    ]
    active = (
        any(path.exists() for path in settings_candidates)
        or (project_root / "CLAUDE.md").exists()
    )
    if not active:
        return "skip", findings, fixes, proposals

    for settings_path in settings_candidates:
        if not settings_path.exists():
            continue
        path_findings, path_fixes = fix_settings_hook_paths(
            project_root, settings_path, apply_changes=apply_changes
        )
        findings.extend(path_findings)
        fixes.extend(path_fixes)
        hook_findings, hook_fixes = ensure_hook_scripts(
            project_root, settings_path, apply_changes=apply_changes
        )
        findings.extend(hook_findings)
        fixes.extend(hook_fixes)

    v1_findings, v1_fixes = check_v1_hook_null_guards(
        project_root, apply_changes=apply_changes
    )
    findings.extend(v1_findings)
    fixes.extend(v1_fixes)

    claude_md = project_root / "CLAUDE.md"
    if not claude_md.exists():
        template_sources = [
            FRAMEWORK_ROOT / "templates" / "spoke" / "CLAUDE.md",
            FRAMEWORK_ROOT / "templates" / "claude" / "CLAUDE.md",
        ]
        template = next((t for t in template_sources if t.exists()), None)
        if template:
            if apply_changes:
                shutil.copy2(template, claude_md)
                fixes.append(
                    {"path": "CLAUDE.md", "action": "created from framework template"}
                )
                path_findings, path_fixes, path_proposals = ensure_claude_convergence(
                    project_root, claude_md, apply_changes=apply_changes
                )
                findings.extend(path_findings)
                fixes.extend(path_fixes)
                proposals.extend(path_proposals)
            else:
                fixes.append(
                    {"path": "CLAUDE.md", "action": "create from framework template"}
                )
        else:
            findings.append(
                {
                    "area": "Claude",
                    "level": "warn",
                    "code": "claude-md-missing",
                    "message": "CLAUDE.md missing",
                }
            )
    else:
        path_findings, path_fixes, path_proposals = ensure_claude_convergence(
            project_root, claude_md, apply_changes=apply_changes
        )
        findings.extend(path_findings)
        fixes.extend(path_fixes)
        proposals.extend(path_proposals)

    cmd_findings, cmd_fixes = ensure_claude_commands(
        project_root, apply_changes=apply_changes
    )
    findings.extend(cmd_findings)
    fixes.extend(cmd_fixes)

    # ── MCP server coverage proposal ────────────────────────────────────────
    mcp_path = project_root / ".mcp.json"
    if not mcp_path.exists() and claude_md.exists():
        proposals.append(
            {
                "area": "Claude",
                "code": "mcp-not-configured",
                "message": "No .mcp.json found — consider configuring MCP servers for enhanced tool capabilities",
                "target_file": ".mcp.json",
                "risk": "low",
                "requires_human_review": True,
            }
        )

    status = "pass" if not any(f["level"] == "fail" for f in findings) else "fail"
    return status, findings, fixes, proposals


def audit_gemini(
    project_root: Path, apply_changes: bool = True
) -> tuple[str, list[dict], list[dict], list[dict]]:
    findings: list[dict] = []
    fixes: list[dict] = []
    proposals: list[dict] = []
    active = (project_root / "GEMINI.md").exists() or (
        project_root / ".gemini"
    ).exists()
    if not active:
        return "skip", findings, fixes, proposals

    md_findings, md_fixes, md_proposals = ensure_gemini_md(
        project_root, apply_changes=apply_changes
    )
    findings.extend(md_findings)
    fixes.extend(md_fixes)
    proposals.extend(md_proposals)

    wake_findings, wake_fixes, wake_proposals = ensure_wakeup_files(
        project_root, apply_changes=apply_changes
    )
    findings.extend(wake_findings)
    fixes.extend(wake_fixes)
    proposals.extend(wake_proposals)

    settings_fixes, _ = ensure_gemini_settings(
        project_root, apply_changes=apply_changes
    )
    fixes.extend(settings_fixes)

    ignore_fixes, _ = ensure_gemini_ignore(project_root, apply_changes=apply_changes)
    fixes.extend(ignore_fixes)

    for path in [
        project_root / "GEMINI.md",
        project_root / "templates" / "spoke" / "GEMINI.md",
        project_root / "templates" / "gemini" / "GEMINI.md",
    ]:
        path_findings, path_fixes, path_proposals = ensure_gemini_convergence(
            project_root, path, apply_changes=apply_changes
        )
        findings.extend(path_findings)
        fixes.extend(path_fixes)
        proposals.extend(path_proposals)

    status = "pass" if not any(f["level"] == "fail" for f in findings) else "fail"
    return status, findings, fixes, proposals


def audit_codex(
    project_root: Path, apply_changes: bool = True
) -> tuple[str, list[dict], list[dict], list[dict]]:
    findings: list[dict] = []
    fixes: list[dict] = []
    proposals: list[dict] = []
    candidates = [
        project_root / "AGENTS.md",
        project_root / "templates" / "codex" / "AGENTS.md",
        project_root / "templates" / "spoke" / "AGENTS.md",
    ]
    active = any(path.exists() for path in candidates)
    if not active:
        return "skip", findings, fixes, proposals

    for path in candidates:
        if not path.exists():
            continue
        path_findings, path_fixes, path_proposals = ensure_agents_thrift(
            project_root, path, apply_changes=apply_changes
        )
        findings.extend(path_findings)
        fixes.extend(path_fixes)
        proposals.extend(path_proposals)

    status = "pass" if not any(f["level"] == "fail" for f in findings) else "fail"
    return status, findings, fixes, proposals


def ensure_wrapper_scripts(
    project_root: Path, apply_changes: bool = True
) -> tuple[list[dict], list[dict]]:
    """Check wai-enter.sh and wai-exit.sh exist and are executable. Apply from template if missing."""
    findings: list[dict] = []
    fixes: list[dict] = []
    wai_spoke = project_root / "WAI-Spoke"
    if not wai_spoke.exists():
        return findings, fixes  # not a WAI project, skip silently

    wrapper_scripts = {
        "wai-enter.sh": FRAMEWORK_ROOT / "templates" / "spoke" / "wai-enter.sh",
        "wai-exit.sh": FRAMEWORK_ROOT / "templates" / "spoke" / "wai-exit.sh",
    }
    for script_name, template_src in wrapper_scripts.items():
        dest = project_root / script_name
        if not dest.exists():
            if template_src.exists():
                if apply_changes:
                    import shutil

                    shutil.copy2(template_src, dest)
                    dest.chmod(dest.stat().st_mode | 0o111)
                    fixes.append(
                        {"path": script_name, "action": f"installed from template"}
                    )
                else:
                    findings.append(
                        {
                            "area": "Shared",
                            "level": "warn",
                            "code": "wrapper-script-missing",
                            "message": f"{script_name} missing — wakeup brief pre-generation unavailable",
                        }
                    )
            else:
                findings.append(
                    {
                        "area": "Shared",
                        "level": "warn",
                        "code": "wrapper-script-missing",
                        "message": f"{script_name} missing and template source not found",
                    }
                )
        else:
            # Exists — ensure executable
            import stat

            mode = dest.stat().st_mode
            if not (mode & stat.S_IXUSR):
                if apply_changes:
                    dest.chmod(mode | 0o111)
                    fixes.append({"path": script_name, "action": "set executable bit"})
                else:
                    findings.append(
                        {
                            "area": "Shared",
                            "level": "warn",
                            "code": "wrapper-script-not-executable",
                            "message": f"{script_name} exists but is not executable",
                        }
                    )
    return findings, fixes


def check_compatibility_redirects(project_root: Path) -> tuple[list[dict], list[dict]]:
    """Verify legacy maximizer skill files redirect to the Tool Advisor."""
    findings: list[dict] = []
    fixes: list[dict] = []
    for rel in MAXIMIZER_REDIRECT_PATHS:
        path = project_root / rel
        if not path.exists():
            continue
        content = read_text(path).lower()
        if (
            "tool advisor" not in content
            and "tool_advisor" not in content
            and "wai-tool-advisor" not in content
        ):
            findings.append(
                {
                    "area": "Shared",
                    "level": "warn",
                    "code": "maximizer-not-redirected",
                    "message": f"{rel} does not redirect to Tool Advisor",
                }
            )
    return findings, fixes


def audit_shared(
    project_root: Path, apply_changes: bool = True
) -> tuple[str, list[dict], list[dict], list[dict]]:
    findings: list[dict] = []
    fixes: list[dict] = []
    proposals: list[dict] = []

    # ── Bootstrap script check ───────────────────────────────────────────────
    target = project_root / "bootstrap" / "spoke-upgrade.sh"
    if target.exists():
        content = read_text(target)
        if "$CLAUDE_PROJECT_DIR/.claude/hooks/user-prompt-submit.sh" in content:
            findings.append(
                {
                    "area": "Shared",
                    "level": "warn",
                    "code": "bootstrap-hook-env-var",
                    "message": "bootstrap/spoke-upgrade.sh still embeds unresolved hook env vars",
                }
            )

    # ── Wrapper script check (wai-enter.sh / wai-exit.sh) ───────────────────
    wrapper_findings, wrapper_fixes = ensure_wrapper_scripts(
        project_root, apply_changes=apply_changes
    )
    findings.extend(wrapper_findings)
    fixes.extend(wrapper_fixes)

    # ── Compatibility redirects ──────────────────────────────────────────────
    compat_findings, compat_fixes = check_compatibility_redirects(project_root)
    findings.extend(compat_findings)
    fixes.extend(compat_fixes)

    # ── Cross-tool coverage proposals ───────────────────────────────────────
    has_gemini = (project_root / "GEMINI.md").exists()
    has_agents = (project_root / "AGENTS.md").exists()
    has_claude = (project_root / "CLAUDE.md").exists()
    if has_agents and not has_gemini and has_claude:
        proposals.append(
            {
                "area": "Shared",
                "code": "gemini-coverage-absent",
                "message": "AGENTS.md present but GEMINI.md absent — consider adding GEMINI.md for Gemini CLI coverage",
                "target_file": "GEMINI.md",
                "risk": "low",
                "requires_human_review": True,
            }
        )
    if has_gemini and not has_agents and has_claude:
        proposals.append(
            {
                "area": "Shared",
                "code": "codex-coverage-absent",
                "message": "GEMINI.md present but AGENTS.md absent — consider adding AGENTS.md for Codex/OpenAI coverage",
                "target_file": "AGENTS.md",
                "risk": "low",
                "requires_human_review": True,
            }
        )

    # Skip if nothing was checked (not a WAI project and no bootstrap)
    if not target.exists() and not (project_root / "WAI-Spoke").exists():
        return "skip", findings, fixes, proposals

    status = "pass" if not any(f["level"] == "fail" for f in findings) else "fail"
    return status, findings, fixes, proposals


def mark_stale_if_needed(project_root: Path, session_id: str | None = None) -> dict:
    advisor_dir, state = ensure_advisor_layout(project_root)
    fingerprint, entries = collect_fingerprint(project_root)
    reasons: list[str] = []

    last_fingerprint = state.get("last_fingerprint", "")
    if last_fingerprint and last_fingerprint != fingerprint:
        changed = [
            rel
            for rel, digest in entries.items()
            if state.get("fingerprint_entries", {}).get(rel) != digest
        ]
        if changed:
            reasons.append("config drift: " + ", ".join(changed[:5]))
        state["last_drift_at"] = now_iso()
    elif not state.get("last_audit_at"):
        reasons.append("never audited")

    if session_id and session_id != state.get("last_observed_session"):
        state["last_observed_session"] = session_id
        state["sessions_since_last_audit"] = (
            state.get("sessions_since_last_audit", 0) + 1
        )

    last_audit = parse_ts(state.get("last_audit_at"))
    if last_audit and datetime.now(timezone.utc) - last_audit >= timedelta(days=7):
        reasons.append("audit older than 7 days")

    if state.get("sessions_since_last_audit", 0) >= 10:
        reasons.append("10 sessions since last audit")

    if reasons:
        state["audit_pending"] = True
        state["audit_reason"] = "; ".join(dict.fromkeys(reasons))

    state["last_fingerprint"] = fingerprint
    state["fingerprint_entries"] = entries
    write_json(advisor_dir / "scan_state.json", state)
    return {
        "advisor_id": "tool-advisor",
        "audit_pending": state.get("audit_pending", False),
        "audit_reason": state.get("audit_reason"),
        "sessions_since_last_audit": state.get("sessions_since_last_audit", 0),
    }


def run_audit(
    project_root: Path, session_id: str | None = None, apply_changes: bool = True
) -> dict:
    advisor_dir, state = ensure_advisor_layout(project_root, create=apply_changes)
    areas = {
        "Claude": audit_claude,
        "Gemini": audit_gemini,
        "Codex": audit_codex,
        "Shared": audit_shared,
    }
    all_findings: list[dict] = []
    all_fixes: list[dict] = []
    all_proposals: list[dict] = []
    score_by_area: dict[str, str] = {}

    for area, fn in areas.items():
        status, findings, fixes, proposals = fn(
            project_root, apply_changes=apply_changes
        )
        score_by_area[area] = status
        all_findings.extend(findings)
        all_fixes.extend(fixes)
        all_proposals.extend(proposals)

    all_findings = _tag_category(all_findings)

    current_score = sum(1 for status in score_by_area.values() if status == "pass")
    previous_score = state.get("current_score") or 0
    score_delta = current_score - previous_score

    audit_ts = now_iso()
    state["last_audit_at"] = audit_ts
    state["last_audit_session"] = session_id
    state["current_score"] = current_score
    state["score_by_area"] = score_by_area
    state["audit_pending"] = False
    state["audit_reason"] = ""
    state["sessions_since_last_audit"] = 0
    state["total_audits"] = state.get("total_audits", 0) + 1
    state["auto_applied_count"] = state.get("auto_applied_count", 0) + len(all_fixes)
    state["pending_proposals"] = all_proposals
    state["last_findings"] = [finding["message"] for finding in all_findings[:8]]

    fingerprint, entries = collect_fingerprint(project_root)
    state["last_fingerprint"] = fingerprint
    state["fingerprint_entries"] = entries
    if apply_changes:
        write_json(advisor_dir / "scan_state.json", state)
        update_schedule_index(project_root, state["last_audit_at"])

    pass_record = {
        "id": f"audit-{datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S')}",
        "ts": state["last_audit_at"],
        "session": session_id,
        "score": current_score,
        "score_by_area": score_by_area,
        "score_delta": score_delta,
        "findings": all_findings,
        "auto_applied": all_fixes,
        "proposals_generated": len(all_proposals),
    }
    if apply_changes:
        append_jsonl(advisor_dir / "passes.jsonl", pass_record)
        _append_vector(advisor_dir, state, session_id, score_delta, all_findings)
        _write_proposal_report(advisor_dir, all_proposals, audit_ts)

    report = {
        "advisor_id": "tool-advisor",
        "version": ADVISOR_VERSION,
        "mode": "update" if apply_changes else "evaluate",
        "project_root": str(project_root),
        "score": current_score,
        "score_by_area": score_by_area,
        "findings": all_findings,
        "auto_applied": all_fixes if apply_changes else [],
        "planned_fixes": [] if apply_changes else all_fixes,
        "proposals": all_proposals,
        "audit_pending": state["audit_pending"],
        "audit_reason": state["audit_reason"],
    }
    if apply_changes:
        write_json(advisor_dir / "reports" / "latest.json", report)
    return report


def migrate_cc_advisor(project_root: Path) -> dict:
    """One-time import of cc-advisor history into tool-advisor state.

    Translates cc-advisor passes into tool-advisor pass format, preserves
    audit counts, and records migration metadata. Idempotent — skips if
    already migrated.
    """
    cc_state_path = (
        project_root / "WAI-Spoke" / "advisors" / "cc-advisor" / "scan_state.json"
    )
    cc_passes_path = (
        project_root / "WAI-Spoke" / "advisors" / "cc-advisor" / "passes.jsonl"
    )

    if not cc_state_path.exists():
        return {"status": "skipped", "reason": "cc-advisor/scan_state.json not found"}

    advisor_dir, state = ensure_advisor_layout(project_root)

    if state.get("cc_advisor_migrated"):
        return {
            "status": "skipped",
            "reason": "cc-advisor already migrated (cc_advisor_migrated=true)",
        }

    cc_state = load_json(cc_state_path, {})
    cc_total_audits = cc_state.get("total_audits", 0)
    cc_auto_applied = cc_state.get("auto_applied_count", 0)

    # Bring over historical totals without double-counting current tool-advisor runs.
    state["total_audits"] = max(state.get("total_audits", 0), cc_total_audits)
    state["auto_applied_count"] = state.get("auto_applied_count", 0) + cc_auto_applied
    state["cc_advisor_migrated"] = True
    state["cc_advisor_migrated_at"] = now_iso()
    state["cc_advisor_last_audit_at"] = cc_state.get("last_audit_at")
    state["cc_advisor_last_score"] = cc_state.get("current_score")

    migrated_count = 0
    if cc_passes_path.exists():
        with cc_passes_path.open() as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                try:
                    record = json.loads(line)
                except json.JSONDecodeError:
                    continue
                # Translate cc-advisor area schema to tool-advisor area schema.
                # cc-advisor tracks {CLAUDE.md, Hooks, Permissions, ...} while
                # tool-advisor tracks {Claude, Gemini, Codex, Shared}.
                translated: dict = {
                    "id": record.get("id", f"cc-migrated-{migrated_count}"),
                    "ts": record.get("ts"),
                    "session": record.get("session"),
                    "score": record.get("score"),
                    "score_by_area": {
                        "Claude": "pass" if record.get("score", 0) > 0 else "fail",
                        "Gemini": "skip",
                        "Codex": "skip",
                        "Shared": "skip",
                    },
                    "score_delta": record.get("score_delta", 0),
                    "findings": record.get("findings", []),
                    "proposals_generated": record.get("proposals_generated", 0),
                    "migrated_from": "cc-advisor",
                    "original_score_by_area": record.get("score_by_area", {}),
                }
                append_jsonl(advisor_dir / "passes.jsonl", translated)
                migrated_count += 1

    write_json(advisor_dir / "scan_state.json", state)
    return {
        "status": "ok",
        "passes_migrated": migrated_count,
        "cc_total_audits": cc_total_audits,
        "cc_auto_applied": cc_auto_applied,
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Cross-tool advisor audit and safe remediation"
    )
    parser.add_argument(
        "--root", default=".", help="Project root (default: current directory)"
    )
    parser.add_argument(
        "--mark-stale-if-needed", action="store_true", help="Cheap hook-safe mode"
    )
    parser.add_argument(
        "--evaluate-only",
        action="store_true",
        help="Dry-run audit without changing files",
    )
    parser.add_argument(
        "--migrate-cc-advisor",
        action="store_true",
        help="One-time import of cc-advisor history",
    )
    parser.add_argument("--session-id", help="Session ID for stale tracking")
    parser.add_argument("--json", action="store_true", help="Emit JSON only")
    args = parser.parse_args()

    project_root = Path(args.root).resolve()
    if not (project_root / "WAI-Spoke").exists():
        payload = {"error": f"No WAI-Spoke/ found at {project_root}"}
        if args.json:
            print(json.dumps(payload, indent=2))
            return 1
        print(payload["error"], file=sys.stderr)
        return 1

    if args.migrate_cc_advisor:
        result = migrate_cc_advisor(project_root)
    elif args.mark_stale_if_needed:
        result = mark_stale_if_needed(project_root, args.session_id)
    else:
        result = run_audit(
            project_root, args.session_id, apply_changes=not args.evaluate_only
        )

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(json.dumps(result))
    return 0


if __name__ == "__main__":
    sys.exit(main())
