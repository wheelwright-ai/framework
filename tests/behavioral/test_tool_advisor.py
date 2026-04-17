"""
Behavioral tests for the cross-tool advisor.
"""

import json
import subprocess
import sys
from pathlib import Path


FRAMEWORK_ROOT = Path(__file__).parent.parent.parent
TOOL_ADVISOR = FRAMEWORK_ROOT / "tools" / "tool_advisor.py"


def run_tool_advisor(spoke_root: Path, *args: str) -> dict:
    result = subprocess.run(
        [sys.executable, str(TOOL_ADVISOR), "--root", str(spoke_root), *args, "--json"],
        capture_output=True,
        text=True,
        check=True,
    )
    return json.loads(result.stdout)


def test_tool_advisor_safe_fixes_gemini_and_hook_paths(tmp_spoke):
    (tmp_spoke / "AGENTS.md").write_text(
        "# Instructions\n\nRead `WAI-Spoke/WAI-Guide.md` for the skill index and command map.\n"
    )
    (tmp_spoke / "GEMINI.md").write_text(
        "# Gemini\n\n## Session Start\n\n1. Read `AGENTS.md`.\n2. Follow `WAI-Spoke/skills/wai/wai.md`.\n"
    )

    wai_skill = tmp_spoke / "WAI-Spoke" / "skills" / "wai"
    wai_skill.mkdir(parents=True, exist_ok=True)
    (wai_skill / "wai.md").write_text(
        "# WAI\n\n## Step 1: Load Integration File\n\nDetect environment and read the integration file.\n\n## Step 5: Discover Teachings\n\nScan for teachings.\n"
    )
    wai_commands = tmp_spoke / "WAI-Spoke" / "commands"
    wai_commands.mkdir(parents=True, exist_ok=True)
    (wai_commands / "wai.md").write_text(
        "# WAI\n\n## Step 5: Discover Teachings\n\nScan for teachings.\n"
    )

    hooks_dir = tmp_spoke / ".claude" / "hooks"
    hooks_dir.mkdir(parents=True, exist_ok=True)
    (hooks_dir / "user-prompt-submit.sh").write_text("#!/bin/bash\nexit 0\n")
    (tmp_spoke / ".claude" / "settings.json").write_text(
        json.dumps(
            {
                "hooks": {
                    "UserPromptSubmit": [
                        {
                            "matcher": ".*",
                            "hooks": [
                                {
                                    "type": "command",
                                    "command": "$CLAUDE_PROJECT_DIR/.claude/hooks/user-prompt-submit.sh",
                                }
                            ],
                        }
                    ],
                    "PreToolUse": [
                        {
                            "matcher": "Bash",
                            "hooks": [
                                {
                                    "type": "command",
                                    "command": "./.claude/hooks/pre-tool-guard.sh",
                                }
                            ],
                        }
                    ]
                }
            },
            indent=2,
        )
        + "\n"
    )

    report = run_tool_advisor(tmp_spoke)

    settings = json.loads((tmp_spoke / ".claude" / "settings.json").read_text())
    command = settings["hooks"]["UserPromptSubmit"][0]["hooks"][0]["command"]
    assert "$CLAUDE_PROJECT_DIR" not in command
    assert command == str(tmp_spoke / ".claude" / "hooks" / "user-prompt-submit.sh")
    assert (tmp_spoke / ".claude" / "hooks" / "pre-tool-guard.sh").exists()

    gemini_settings = json.loads((tmp_spoke / ".gemini" / "settings.json").read_text())
    assert gemini_settings["context"]["fileName"] == ["GEMINI.md", "AGENTS.md"]

    gemini_ignore = (tmp_spoke / ".geminiignore").read_text()
    assert "WAI-Spoke/sessions/" in gemini_ignore

    gemini_md = (tmp_spoke / "GEMINI.md").read_text()
    assert "Treat this `GEMINI.md` read as already satisfying" in gemini_md
    assert "Do not re-read `GEMINI.md`" in gemini_md

    wai_md = (wai_skill / "wai.md").read_text().lower()
    assert "do not reopen the same integration file during wakeup" in wai_md
    assert "finish the wai point briefing before" in wai_md
    assert "do not read full teaching bodies unless the user explicitly asks" in wai_md
    assert "do not replace the briefing with a numbered next-steps plan" in wai_md

    wai_commands_md = (wai_commands / "wai.md").read_text().lower()
    assert "finish the wai point briefing before" in wai_commands_md
    assert "do not replace the briefing with a numbered next-steps plan" in wai_commands_md

    agents_md = (tmp_spoke / "AGENTS.md").read_text()
    assert "WAI-Guide.md" not in agents_md
    assert "WAI-Spoke/commands/wai.md" in agents_md
    assert "Finish the WAI Point briefing before asking for approval" in agents_md
    assert "Do not append a numbered next-steps plan" in agents_md

    scan_state = json.loads(
        (tmp_spoke / "WAI-Spoke" / "advisors" / "tool-advisor" / "scan_state.json").read_text()
    )
    assert scan_state["audit_pending"] is False
    assert report["score_by_area"]["Gemini"] == "pass"


def test_tool_advisor_marks_stale_on_drift(tmp_spoke):
    (tmp_spoke / "AGENTS.md").write_text("# AGENTS\n")
    run_tool_advisor(tmp_spoke)

    (tmp_spoke / "AGENTS.md").write_text("# AGENTS\n\nUpdated.\n")
    stale = run_tool_advisor(tmp_spoke, "--mark-stale-if-needed", "--session-id", "session-1")

    assert stale["audit_pending"] is True
    assert "config drift" in stale["audit_reason"]
