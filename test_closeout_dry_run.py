#!/usr/bin/env python3
"""Test closeout workflow (dry-run mode)."""

from wai.closeout import CloseoutWorkflow
import json

# Run closeout in dry-run mode
workflow = CloseoutWorkflow(repo_path=".", dry_run=True)
summary = workflow.execute(message="Test: observation system implementation")

print("\nCloseout Execution Summary:")
print(json.dumps(summary, indent=2, default=str))

# Check observations were logged
logger = workflow.logger
all_obs = logger._read_all()
print(f"\n✓ Total observations logged: {len(all_obs)}")

if all_obs:
    recent = all_obs[-1]
    print(f"✓ Most recent observation:")
    print(f"  Action: {recent['action']['id']}")
    print(f"  Status: {recent['status']}")
    print(f"  Timestamp: {recent['timestamp']}")
