#!/usr/bin/env python3
"""
Test Spoke Factory

Utilities for creating test spokes and hubs with realistic configurations
for idempotency testing scenarios.
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, List, Optional


def create_test_spoke(
    spoke_dir: Path,
    project_name: str = "test-project",
    framework_version: str = "2.0.17",
    session_count: int = 1,
    has_active_work: bool = False,
) -> Path:
    """
    Create a realistic test spoke directory structure.

    Args:
        spoke_dir: Directory to create spoke in
        project_name: Name of the project
        framework_version: Framework version to simulate
        session_count: Number of previous sessions
        has_active_work: Whether to include open lugs

    Returns:
        Path to the created spoke directory
    """
    # Create directory structure
    spoke_dir.mkdir(parents=True, exist_ok=True)
    wai_spoke = spoke_dir / "WAI-Spoke"
    wai_spoke.mkdir(exist_ok=True)

    # Create subdirectories
    for subdir in ["sessions", "commands", "seed/ingest/processed", "lugs/outbox"]:
        (wai_spoke / subdir).mkdir(parents=True, exist_ok=True)

    # Create WAI-State.json
    state = {
        "wheel": {
            "version": "0.1.0",
            "node_type": "spoke",
            "name": project_name,
            "hub_id": "TestHub",
            "description": f"Test spoke for {project_name}",
            "created": "2026-03-15T10:00:00Z",
            "last_modified": "2026-03-19T09:00:00Z",
            "hub_path": None,  # Will be set by tests if needed
            "status": "active",
            "framework_version": framework_version,
        },
        "_project_foundation": {
            "completed": True,
            "identity": {
                "type": "test",
                "name": project_name,
                "one_liner": f"Test project for {project_name}",
                "success_looks_like": "Tests pass and behavior is verified",
            },
            "boundaries": {
                "in_scope": ["Testing idempotency"],
                "out_of_scope": ["Production deployment"],
                "constraints": ["Test environment only"],
            },
        },
        "_session_state": {
            "last_session_id": f"session-20260319-{session_count:04d}",
            "last_modified_by": "test-agent",
            "last_modified_at": "2026-03-19T10:00:00Z",
            "last_closeout": "2026-03-19T09:30:00Z",
            "session_count": session_count,
            "protocol_completed": True,
            "requires_review": False,
            "mode": "execution",
        },
    }

    state_file = wai_spoke / "WAI-State.json"
    with open(state_file, "w") as f:
        json.dump(state, f, indent=2)

    # Create empty WAI-Lugs.jsonl
    lugs_file = wai_spoke / "WAI-Lugs.jsonl"
    lugs_file.touch()

    # Add active work if requested
    if has_active_work:
        add_test_lugs(
            lugs_file,
            [
                {
                    "i": "test-work-001",
                    "ty": "task",
                    "t": "Test task in progress",
                    "s": "p",
                    "ca": "2026-03-19T09:00:00Z",
                    "gb": "test-agent",
                }
            ],
        )

    # Create empty signals file
    signals_file = wai_spoke / "WAI-Signals.jsonl"
    with open(signals_file, "w") as f:
        f.write("# RETIRED: Absorbed into WAI-Lugs.jsonl as of WAI v2 migration.\n")
        f.write(
            "# Do not use this file. All signals are now Lugs with impact >= 8.\n\n"
        )

    # Initialize git repository if not exists
    git_dir = spoke_dir / ".git"
    if not git_dir.exists():
        os.system(
            f"cd {spoke_dir} && git init && git config user.name 'Test' && git config user.email 'test@example.com'"
        )
        os.system(f"cd {spoke_dir} && git add . && git commit -m 'Initial test spoke'")

    return spoke_dir


def create_test_hub(hub_dir: Path) -> Path:
    """
    Create a test hub directory structure.

    Args:
        hub_dir: Directory to create hub in

    Returns:
        Path to the created hub directory
    """
    hub_dir.mkdir(parents=True, exist_ok=True)

    # Create hub subdirectories
    for subdir in [
        "teachings",
        "WAI-Spoke/lugs/inbox",
        "WAI-Hub/Signals/incoming",
        "WAI-Hub/Signals/processed",
    ]:
        (hub_dir / subdir).mkdir(parents=True, exist_ok=True)

    # Create hub profile
    profile = {
        "hub_id": "test-hub",
        "created_at": "2026-03-15T10:00:00Z",
        "description": "Test hub for idempotency testing",
        "spokes_count": 0,
    }

    profile_file = hub_dir / "hub-profile.json"
    with open(profile_file, "w") as f:
        json.dump(profile, f, indent=2)

    return hub_dir


def add_test_lugs(lugs_file: Path, lugs: List[Dict[str, Any]]):
    """
    Add test lugs to a WAI-Lugs.jsonl file.

    Args:
        lugs_file: Path to WAI-Lugs.jsonl file
        lugs: List of lug dictionaries to add
    """
    with open(lugs_file, "a") as f:
        for lug in lugs:
            f.write(json.dumps(lug) + "\n")


def create_test_work_scenario(spoke_dir: Path, scenario: str):
    """
    Create specific work scenarios for testing.

    Args:
        spoke_dir: Spoke directory
        scenario: Scenario name ('autosave_pending', 'high_impact_decision', etc.)
    """
    lugs_file = spoke_dir / "WAI-Spoke" / "WAI-Lugs.jsonl"

    scenarios = {
        "autosave_pending": [
            {
                "i": "autosave-001",
                "ty": "autosave",
                "t": "Work checkpoint 1",
                "s": "o",
                "ca": "2026-03-19T10:00:00Z",
                "reconciled": False,
            },
            {
                "i": "autosave-002",
                "ty": "autosave",
                "t": "Work checkpoint 2",
                "s": "o",
                "ca": "2026-03-19T10:05:00Z",
                "reconciled": False,
            },
        ],
        "high_impact_decision": [
            {
                "i": "decision-001",
                "ty": "decision",
                "t": "Architecture change decision",
                "s": "c",
                "ca": "2026-03-19T09:30:00Z",
                "gb": "test-agent",
                "impact": 9,
                "resolution": "Adopted microservices pattern for better scalability",
            }
        ],
        "mixed_work": [
            {
                "i": "task-001",
                "ty": "task",
                "t": "Implement feature X",
                "s": "p",
                "ca": "2026-03-19T09:00:00Z",
                "gb": "test-agent",
            },
            {
                "i": "bug-001",
                "ty": "bug",
                "t": "Fix authentication issue",
                "s": "o",
                "ca": "2026-03-19T08:30:00Z",
                "gb": "test-agent",
            },
            {
                "i": "autosave-001",
                "ty": "autosave",
                "t": "Progress save",
                "s": "o",
                "ca": "2026-03-19T10:00:00Z",
                "reconciled": False,
            },
        ],
    }

    if scenario in scenarios:
        add_test_lugs(lugs_file, scenarios[scenario])


def create_migration_test_spokes(
    base_dir: Path, spoke_configs: List[Dict[str, Any]]
) -> List[Path]:
    """
    Create multiple spokes for migration testing.

    Args:
        base_dir: Base directory for all spokes
        spoke_configs: List of spoke configurations

    Returns:
        List of created spoke directory paths
    """
    spoke_dirs = []

    for i, config in enumerate(spoke_configs):
        spoke_name = config.get("name", f"spoke-{i}")
        spoke_dir = base_dir / spoke_name

        create_test_spoke(
            spoke_dir,
            project_name=spoke_name,
            framework_version=config.get("framework_version", "2.0.15"),
            session_count=config.get("session_count", 1),
            has_active_work=config.get("has_active_work", False),
        )

        spoke_dirs.append(spoke_dir)

    return spoke_dirs


def simulate_partial_closeout(spoke_dir: Path):
    """
    Simulate a partially completed closeout operation.

    Args:
        spoke_dir: Spoke directory to modify
    """
    lugs_file = spoke_dir / "WAI-Spoke" / "WAI-Lugs.jsonl"

    # Add some autosave lugs marked as reconciled (partial completion)
    reconciled_autosaves = [
        {
            "i": "autosave-001",
            "ty": "autosave",
            "t": "Checkpoint 1",
            "s": "c",
            "ca": "2026-03-19T10:00:00Z",
            "reconciled": True,
        },
        {
            "i": "autosave-002",
            "ty": "autosave",
            "t": "Checkpoint 2",
            "s": "o",
            "ca": "2026-03-19T10:05:00Z",
            "reconciled": False,  # Not yet reconciled
        },
    ]

    add_test_lugs(lugs_file, reconciled_autosaves)


def verify_spoke_structure(spoke_dir: Path) -> Dict[str, bool]:
    """
    Verify that a spoke has the expected directory structure.

    Args:
        spoke_dir: Spoke directory to verify

    Returns:
        Dictionary of verification results
    """
    wai_spoke = spoke_dir / "WAI-Spoke"

    checks = {
        "wai_spoke_exists": wai_spoke.exists(),
        "state_json_exists": (wai_spoke / "WAI-State.json").exists(),
        "lugs_jsonl_exists": (wai_spoke / "WAI-Lugs.jsonl").exists(),
        "signals_jsonl_exists": (wai_spoke / "WAI-Signals.jsonl").exists(),
        "sessions_dir_exists": (wai_spoke / "sessions").exists(),
        "commands_dir_exists": (wai_spoke / "commands").exists(),
        "git_initialized": (spoke_dir / ".git").exists(),
    }

    # Verify state JSON is valid
    if checks["state_json_exists"]:
        try:
            with open(wai_spoke / "WAI-State.json") as f:
                json.load(f)
            checks["state_json_valid"] = True
        except json.JSONDecodeError:
            checks["state_json_valid"] = False

    return checks


def cleanup_test_environment(base_dir: Path):
    """
    Clean up test environment.

    Args:
        base_dir: Base directory to clean up
    """
    import shutil

    if base_dir.exists():
        shutil.rmtree(base_dir, ignore_errors=True)


# Configuration presets for common test scenarios
TEST_SPOKE_PRESETS = {
    "basic": {
        "framework_version": "2.0.17",
        "session_count": 1,
        "has_active_work": False,
    },
    "with_work": {
        "framework_version": "2.0.17",
        "session_count": 3,
        "has_active_work": True,
    },
    "old_version": {
        "framework_version": "2.0.15",
        "session_count": 10,
        "has_active_work": True,
    },
    "migration_candidate": {
        "framework_version": "2.0.16",
        "session_count": 5,
        "has_active_work": False,
    },
}


def create_test_spoke_from_preset(spoke_dir: Path, preset: str, **overrides) -> Path:
    """
    Create test spoke from a preset configuration.

    Args:
        spoke_dir: Directory to create spoke in
        preset: Preset name from TEST_SPOKE_PRESETS
        **overrides: Override any preset values

    Returns:
        Path to created spoke directory
    """
    if preset not in TEST_SPOKE_PRESETS:
        raise ValueError(f"Unknown preset: {preset}")

    config = {**TEST_SPOKE_PRESETS[preset], **overrides}

    return create_test_spoke(spoke_dir, **config)
