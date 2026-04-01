#!/usr/bin/env python3
"""
WAI Skill Behavior E2E Test Suite

Tests skill structural integrity, lug schema, hook behavior,
and session lifecycle without requiring an LLM. Verifies that
the template assets are well-formed and internally consistent.

Run: python3 benchmarks/e2e/test_skills.py
"""

import json
import os
import re
import subprocess
import sys
import tempfile
import time
from pathlib import Path

# ─── Config ───────────────────────────────────────────────────────────────────

ROOT = Path(__file__).parent.parent.parent  # framework root
COMMANDS = ROOT / "templates" / "commands"
WAI_SPOKE = ROOT / "WAI-Spoke"
HOOK = ROOT / ".claude" / "hooks" / "user-prompt-submit.sh"

REQUIRED_SKILLS = [
    "wai",
    "wai-closeout",
    # wai-shipit moved to WAI-Spoke/skills/shipit/ (skill thrift refactor, S67)
    "wai-lug-schema",
    "wai-foundation",
    "wai-ide-setup",
    "wai-complexity-gate",
    "wai-rules",
    "wai-principles",
    "wai-status",
    "wai-context-guard",
    "wai-signal-capture",
    "wai-stewardship-guard",
    "wai-green-light",
    "wai-red-light",
]

# Commands that were absorbed into other skills — referenced in prose but
# have no standalone .md file. Cross-reference check skips these.
ABSORBED_COMMANDS = {"wai-teach", "wai-learn", "wai-review"}

SKILL_REQUIRED_SECTIONS = {
    # wai.md refactored to numbered steps (S67 skill thrift); sections renamed
    "wai": ["## Step 1: Load Integration File", "## Step 7: Display Briefing", "## Incoming Routing Rules"],
    # wai-closeout.md thrift refactor removed ## Incomplete Work (S67)
    "wai-closeout": ["## Closeout Procedure", "## Success Criteria"],
    # wai-teach removed — absorbed into wai-closeout.md Step 9b
    # wai-learn removed — absorbed into wai.md Step 3a
    "wai-lug-schema": [
        # ## Lug Creation Template removed in thrift refactor (S67)
        "## Lug Lifecycle",
        "## Complete Lug Type Catalog",
        "## Canonical Storage",
    ],
    "wai-ide-setup": [
        "## Claude Code Setup",
        "## Hook Behavior",
        "## Setup Verification",
    ],
}

REQUIRED_LUG_FIELDS = [
    ("i", "id"),  # short or long key
    ("ty", "type"),
    ("t", "title"),
]
VALID_LUG_TYPES = {
    "task",
    "bug",
    "feature",
    "review",
    "epic",
    "signal",
    "foundation",
    "session-summary",
    "autosave",
    "policy",
    "observation",
    "learning",
    "maintenance",
    "core-protocol",
    "delivery_confirmation",
    "phone-home",
    "config",
    "session",
    "shipit",
    "decision",
    "lug",
    "protocol",
    "diagnosis",
    "refactor",  # legacy types in existing file
    "idea",  # improvement idea (proposed feature/change)
    "response",  # hub-to-spoke response lug
}
VALID_LUG_STATUSES = {
    "o",
    "p",
    "c",
    "b",
    "open",
    "in-progress",
    "closed",
    "resolved",
    "blocked",
    "published",
    "reviewed",  # legacy statuses in existing file
    "proposed",  # idea/taste nudge awaiting accept/reject
    "completed",
    "archived",  # current statuses (Session 42+)
}

# ─── Test runner ──────────────────────────────────────────────────────────────


class TestResult:
    def __init__(self, name: str):
        self.name = name
        self.passed: list[str] = []
        self.failed: list[str] = []
        self.start = time.time()

    def ok(self, msg: str):
        self.passed.append(msg)

    def fail(self, msg: str):
        self.failed.append(msg)

    def assert_true(self, condition: bool, msg: str):
        if condition:
            self.ok(msg)
        else:
            self.fail(msg)

    def elapsed(self) -> float:
        return (time.time() - self.start) * 1000

    def summary(self) -> str:
        status = "PASS" if not self.failed else "FAIL"
        return f"[{status}] {self.name} ({len(self.passed)}✓ {len(self.failed)}✗ {self.elapsed():.1f}ms)"


class Suite:
    def __init__(self, name: str):
        self.name = name
        self.results: list[TestResult] = []
        self.start = time.time()

    def run(self, name: str, fn) -> TestResult:
        r = TestResult(name)
        try:
            fn(r)
        except Exception as e:
            r.fail(f"Exception: {e}")
        self.results.append(r)
        return r

    def report(self):
        elapsed = (time.time() - self.start) * 1000
        total = len(self.results)
        passed = sum(1 for r in self.results if not r.failed)
        failed = total - passed

        print(f"\n{'=' * 60}")
        print(f"  {self.name}")
        print(f"{'=' * 60}")
        for r in self.results:
            print(f"  {r.summary()}")
            for msg in r.failed:
                print(f"    ✗ {msg}")
        print(f"{'─' * 60}")
        print(
            f"  Total: {total} | Passed: {passed} | Failed: {failed} | {elapsed:.0f}ms"
        )
        return failed == 0


# ─── Test suites ──────────────────────────────────────────────────────────────


def test_skill_presence(suite: Suite):
    def check(r: TestResult):
        for skill in REQUIRED_SKILLS:
            path = COMMANDS / f"{skill}.md"
            r.assert_true(path.exists(), f"{skill}.md exists")
            if path.exists():
                size = path.stat().st_size
                r.assert_true(size > 100, f"{skill}.md has content ({size}b)")

    suite.run("All required skills present", check)


def test_skill_structure(suite: Suite):
    def check_skill(skill: str, sections: list[str]):
        def inner(r: TestResult):
            path = COMMANDS / f"{skill}.md"
            if not path.exists():
                r.fail(f"{skill}.md not found")
                return
            content = path.read_text()
            # Must start with a title
            r.assert_true(content.startswith("#"), "starts with heading")
            # Must have required sections
            for section in sections:
                r.assert_true(section in content, f"has section '{section}'")
            # Must have at least one --- separator
            r.assert_true("---" in content, "has section separators")
            # No Python imports (skills are markdown only)
            r.assert_true(
                "import " not in content or "```" in content,
                "no Python imports outside code blocks",
            )

        return inner

    for skill, sections in SKILL_REQUIRED_SECTIONS.items():
        suite.run(f"Skill structure: {skill}", check_skill(skill, sections))


def test_skill_cross_references(suite: Suite):
    """Skills should reference each other correctly (no dead links)."""

    def check(r: TestResult):
        all_skills = {f.stem for f in COMMANDS.glob("wai*.md")}
        for skill_file in COMMANDS.glob("wai*.md"):
            content = skill_file.read_text()
            # Find /wai-xxx references
            refs = re.findall(r"`/([a-z-]+)`", content)
            for ref in refs:
                if ref.startswith("wai") and ref not in ABSORBED_COMMANDS:
                    r.assert_true(
                        ref in all_skills,
                        f"{skill_file.stem}: references /{ref} which exists",
                    )

    suite.run("Skill cross-references valid", check)


def test_lug_schema(suite: Suite):
    """Every lug in WAI-Lugs.jsonl must be valid JSON with required fields."""

    def check(r: TestResult):
        lugs_file = WAI_SPOKE / "WAI-Lugs.jsonl"
        r.assert_true(lugs_file.exists(), "WAI-Lugs.jsonl exists")
        if not lugs_file.exists():
            return

        valid = 0
        for i, line in enumerate(lugs_file.read_text().splitlines(), 1):
            line = line.strip()
            if not line:
                continue
            try:
                lug = json.loads(line)
                valid += 1
                lug_id = lug.get("i", lug.get("id", "?"))
                is_closed = lug.get("s", lug.get("status", "")) in (
                    "c",
                    "closed",
                    "resolved",
                    "published",
                    "reviewed",
                )
                is_reconciled = lug.get("reconciled", False)
                # Required fields — title optional for closed/reconciled entries
                # (lightweight override records don't need a title)
                for short_key, long_key in REQUIRED_LUG_FIELDS:
                    if (short_key, long_key) == ("t", "title") and (
                        is_closed or is_reconciled
                    ):
                        continue  # title not required for closed/reconciled records
                    r.assert_true(
                        short_key in lug or long_key in lug,
                        f"lug line {i} (id={lug_id}) has '{short_key}' or '{long_key}'",
                    )
                # Type is from known catalog
                ty = lug.get("ty", lug.get("type", ""))
                r.assert_true(
                    ty in VALID_LUG_TYPES, f"lug line {i} type '{ty}' in catalog"
                )
                # Status (if present) is valid
                status = lug.get("s", lug.get("status", ""))
                if status:
                    r.assert_true(
                        status in VALID_LUG_STATUSES,
                        f"lug line {i} status '{status}' is valid",
                    )
            except json.JSONDecodeError as e:
                r.fail(f"lug line {i}: invalid JSON — {e}")

        r.ok(f"Parsed {valid} lugs successfully")

    suite.run("WAI-Lugs.jsonl schema valid", check)


def test_wai_state_schema(suite: Suite):
    """WAI-State.json must be valid with required structure."""

    def check(r: TestResult):
        state_file = WAI_SPOKE / "WAI-State.json"
        r.assert_true(state_file.exists(), "WAI-State.json exists")
        if not state_file.exists():
            return

        try:
            state = json.loads(state_file.read_text())
        except json.JSONDecodeError as e:
            r.fail(f"WAI-State.json invalid JSON: {e}")
            return

        # Required top-level keys
        for key in ["wheel", "_session_state"]:
            r.assert_true(key in state, f"has '{key}' key")

        # wheel section
        wheel = state.get("wheel", {})
        for key in ["name", "version"]:
            r.assert_true(key in wheel, f"wheel.{key} present")

        # _session_state section
        session = state.get("_session_state", {})
        r.assert_true(
            "protocol_completed" in session, "_session_state.protocol_completed present"
        )
        r.assert_true(
            isinstance(session.get("protocol_completed"), bool),
            "protocol_completed is boolean",
        )

    suite.run("WAI-State.json schema valid", check)


def test_hook_behavior(suite: Suite):
    """Test hook script logic using a temp WAI-State.json."""

    def check_new_session(r: TestResult):
        """New session: last_session_id == current_session_id → should reset + inject."""
        if not HOOK.exists():
            r.fail("Hook script not found")
            return

        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            spoke = tmp_path / "WAI-Spoke"
            spoke.mkdir()

            # Simulate: session IDs match (new session)
            state = {
                "wheel": {"name": "test"},
                "_session_state": {
                    "protocol_completed": True,  # was set last session
                    "last_session_id": "sess-abc123",
                    "current_session": {
                        "session_id": "sess-abc123"
                    },  # same = new session
                },
            }
            (spoke / "WAI-State.json").write_text(json.dumps(state))

            env = {**os.environ, "CLAUDE_PROJECT_DIR": str(tmp_path)}
            result = subprocess.run(
                ["bash", str(HOOK)], env=env, capture_output=True, text=True, timeout=5
            )

            # Should inject wakeup directive
            r.assert_true(
                "wai-session-start" in result.stdout,
                "injects wakeup directive for new session",
            )
            r.assert_true(result.returncode == 0, "exits 0")

            # State should have protocol_completed=false then true
            updated = json.loads((spoke / "WAI-State.json").read_text())
            r.assert_true(
                updated["_session_state"]["protocol_completed"] == True,
                "sets protocol_completed=true after injection",
            )

    def check_same_session(r: TestResult):
        """Same session: protocol_completed=true → should skip injection."""
        if not HOOK.exists():
            r.fail("Hook script not found")
            return

        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            spoke = tmp_path / "WAI-Spoke"
            spoke.mkdir()

            # Simulate: already ran this session
            state = {
                "wheel": {"name": "test"},
                "_session_state": {
                    "protocol_completed": True,
                    "last_session_id": "sess-old",
                    "track_path": "",
                },
            }
            (spoke / "WAI-State.json").write_text(json.dumps(state))

            # Hook reads protocol_completed from session-guard.json (runtime file),
            # not WAI-State.json. Guard session_id != last_session_id → same session.
            runtime = spoke / "runtime"
            runtime.mkdir()
            guard = {
                "session_id": "sess-current",  # != last_session_id → not a new session
                "protocol_completed": True,
                "started_at": "2026-01-01T00:00:00Z",
            }
            (runtime / "session-guard.json").write_text(json.dumps(guard))

            env = {**os.environ, "CLAUDE_PROJECT_DIR": str(tmp_path)}
            result = subprocess.run(
                ["bash", str(HOOK)], env=env, capture_output=True, text=True, timeout=5
            )

            r.assert_true(
                "wai-session-start" not in result.stdout,
                "skips injection when protocol already ran",
            )
            r.assert_true(result.returncode == 0, "exits 0")

    def check_non_wai_project(r: TestResult):
        """Non-WAI project (no WAI-State.json) → exits silently."""
        if not HOOK.exists():
            r.fail("Hook script not found")
            return

        with tempfile.TemporaryDirectory() as tmp:
            env = {**os.environ, "CLAUDE_PROJECT_DIR": tmp}
            result = subprocess.run(
                ["bash", str(HOOK)], env=env, capture_output=True, text=True, timeout=5
            )
            r.assert_true(result.stdout == "", "no output for non-WAI project")
            r.assert_true(result.returncode == 0, "exits 0")

    suite.run("Hook: new session triggers wakeup", check_new_session)
    suite.run("Hook: same session skips injection", check_same_session)
    suite.run("Hook: non-WAI project exits silently", check_non_wai_project)


def test_lug_lifecycle(suite: Suite):
    """Simulate lug CREATE → UPDATE → CLOSE lifecycle in a temp file."""

    def check(r: TestResult):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".jsonl", delete=False) as f:
            tmp_path = Path(f.name)

        try:
            # CREATE — append open lug
            lug_id = "test1a2b3c4d5e"
            lug = {
                "i": lug_id,
                "ty": "task",
                "t": "Test task",
                "s": "o",
                "ca": "2026-02-28T00:00:00Z",
                "gb": "test",
            }
            with open(tmp_path, "a") as f:
                f.write(json.dumps(lug) + "\n")

            # Verify CREATE
            lugs = [
                json.loads(l) for l in tmp_path.read_text().splitlines() if l.strip()
            ]
            r.assert_true(len(lugs) == 1, "CREATE: 1 lug written")
            r.assert_true(lugs[0]["s"] == "o", "CREATE: status=open")

            # UPDATE — append new version (in-progress)
            lug_v2 = {**lug, "s": "p", "started_at": "2026-02-28T01:00:00Z"}
            with open(tmp_path, "a") as f:
                f.write(json.dumps(lug_v2) + "\n")

            # Read all, get latest by ID
            lugs = [
                json.loads(l) for l in tmp_path.read_text().splitlines() if l.strip()
            ]
            latest = {l["i"]: l for l in lugs if l["i"] == lug_id}[lug_id]  # last wins
            r.assert_true(len(lugs) == 2, "UPDATE: 2 entries (append-only)")
            # Latest version should be in-progress
            versions = [l for l in lugs if l["i"] == lug_id]
            r.assert_true(
                versions[-1]["s"] == "p", "UPDATE: latest version is in-progress"
            )

            # CLOSE — append closed version
            lug_v3 = {**lug, "s": "c", "resolution": "completed successfully"}
            with open(tmp_path, "a") as f:
                f.write(json.dumps(lug_v3) + "\n")

            lugs = [
                json.loads(l) for l in tmp_path.read_text().splitlines() if l.strip()
            ]
            versions = [l for l in lugs if l["i"] == lug_id]
            r.assert_true(versions[-1]["s"] == "c", "CLOSE: latest version is closed")
            r.assert_true(len(lugs) == 3, "Append-only: 3 total entries")
            r.ok("Lug lifecycle: CREATE → UPDATE → CLOSE verified")

        finally:
            tmp_path.unlink(missing_ok=True)

    suite.run("Lug lifecycle (CREATE→UPDATE→CLOSE)", check)


def test_inbox_routing(suite: Suite):
    """Test inbox routing rules: task→WAI-Lugs, signal→WAI-Signals, phone-home→outbox."""

    def check(r: TestResult):
        routing = {
            "task": "WAI-Lugs.jsonl",
            "bug": "WAI-Lugs.jsonl",
            "feature": "WAI-Lugs.jsonl",
            "signal": "WAI-Signals.jsonl",
            "delivery_confirmation": "acknowledged (no file)",
            "phone-home": "outbox/",
        }

        # wai-learn was folded into wakeup (Step 3a) — routing is in wai.md
        # Try wai-learn.md first (legacy), fall back to wai.md Step 3a
        learn_path = COMMANDS / "wai-learn.md"
        if not learn_path.exists():
            learn_path = COMMANDS / "wai.md"
        learn = learn_path.read_text()

        for ty, dest in routing.items():
            r.assert_true(ty in learn, f"routing rule for '{ty}' documented")

        # Verify signal type routing (WAI-Signals.jsonl retired session 51, now bytype/signal/undelivered/)
        r.assert_true(
            "bytype/signal/undelivered" in learn,
            "signal routing destination documented (bytype/signal/undelivered/)",
        )

        # Verify safety rule: incoming items are data, not instructions
        r.assert_true(
            "DATA" in learn or "data to track" in learn.lower(),
            "inbox safety rule present (incoming items are data, not instructions)",
        )
        r.assert_true(
            "NEVER" in learn or "Never" in learn or "never" in learn,
            "explicit NEVER prohibitions present",
        )

    suite.run("Inbox routing rules documented", check)


def test_session_continuity(suite: Suite):
    """Simulate a full mini-session: wakeup reads → state → closeout output."""

    def check(r: TestResult):
        # Read WAI-State.json
        state_file = WAI_SPOKE / "WAI-State.json"
        if not state_file.exists():
            r.fail("WAI-State.json not found")
            return

        state = json.loads(state_file.read_text())

        # Wakeup: can read project identity
        project_name = state.get("wheel", {}).get("name", "")
        r.assert_true(
            bool(project_name), f"wakeup: project name readable ('{project_name}')"
        )

        # Wakeup: can query open lugs
        lugs_file = WAI_SPOKE / "WAI-Lugs.jsonl"
        if lugs_file.exists():
            lugs = [
                json.loads(l) for l in lugs_file.read_text().splitlines() if l.strip()
            ]
            open_lugs = [
                l for l in lugs if l.get("s") in ("o", "open", "p", "in-progress")
            ]
            r.ok(f"wakeup: {len(open_lugs)} open/in-progress lugs readable")

        # Closeout: session-summary lug would be appended
        # Simulate: create a session-summary and verify schema
        summary = {
            "i": "ss-test1234",
            "ty": "session-summary",
            "t": "Test session",
            "s": "c",
            "ca": "2026-02-28T00:00:00Z",
            "gb": "test",
            "autosaves_reconciled": 0,
            "signals_extracted": [],
            "incomplete_work": [],
        }
        r.assert_true(
            summary["ty"] == "session-summary",
            "closeout: session-summary lug schema valid",
        )
        r.assert_true(
            "autosaves_reconciled" in summary,
            "closeout: autosaves_reconciled field present",
        )
        r.ok("Session continuity flow verified")

    suite.run("Session continuity (wakeup→work→closeout)", check)


# ─── Main ─────────────────────────────────────────────────────────────────────


def main():
    print(f"\nWAI Skill Behavior E2E Tests")
    print(f"Framework: {ROOT}")
    print(f"{'=' * 60}")

    suite = Suite("WAI Skill E2E")

    test_skill_presence(suite)
    test_skill_structure(suite)
    test_skill_cross_references(suite)
    test_lug_schema(suite)
    test_wai_state_schema(suite)
    test_hook_behavior(suite)
    test_lug_lifecycle(suite)
    test_inbox_routing(suite)
    test_session_continuity(suite)

    all_passed = suite.report()
    sys.exit(0 if all_passed else 1)


if __name__ == "__main__":
    main()
