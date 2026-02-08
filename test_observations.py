#!/usr/bin/env python3
"""Test observation system."""

from wai.observation import get_logger
import json

logger = get_logger()

# Log a test observation
obs = logger.log_observation(
    action_id="test.example",
    action_category="test",
    action_description="Test observation logging",
    plan="Verify observation system works",
    command="echo 'test'",
    expected_result={"exit_code": 0},
    actual_result={"exit_code": 0, "stdout": "test", "duration_ms": 50},
    verification={
        "passed": True,
        "checks": [{"name": "exit_code_zero", "passed": True}]
    },
    session_id="test-session-001",
    agent="Test Agent",
    tags=["test", "verification"],
)

print("✓ Observation logged:")
print(f"  ID: {obs['id']}")
print(f"  Action: {obs['action']['id']}")
print(f"  Status: {obs['status']}")
print(f"  Verified: {obs['verification']['passed']}")

# Verify it was written
all_obs = logger._read_all()
print(f"\n✓ Observations file contains {len(all_obs)} observation(s)")

# Test session summary
summary = logger.summarize_session("test-session-001")
print(f"\n✓ Session summary:")
print(f"  Total: {summary['total_observations']}")
print(f"  Passed: {summary['passed']}")
print(f"  Failed: {summary['failed']}")
print(f"  Actions: {summary['actions']}")

# Test idempotency check
already_done = logger.check_already_done("test.example", "test-session-001")
if already_done:
    print(f"\n✓ Idempotency check: Action already done")
    print(f"  Timestamp: {already_done['timestamp']}")
else:
    print("\n✗ Idempotency check failed")
