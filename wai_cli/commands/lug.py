"""
Lug CLI commands for WAI framework.

Provides command-line interface for Lug operations:
- create: Create new Lugs with interactive prompts
- list: List/filter Lugs
- show: Show detailed Lug info
- update: Update Lug fields
- close: Close and archive Lugs
"""

import sys
from pathlib import Path
from typing import Optional

from ..lugs import LugManager
from ..utils.input import print_success, print_error, print_info, print_warning, safe_confirm


def lug_command_group(args: list, spoke_dir: Path):
    """Handle all 'wai lug' commands."""
    if not args or args[0] in ['--help', '-h']:
        _print_lug_help()
        return
    
    subcommand = args[0]
    manager = LugManager(spoke_dir / 'WAI-Spoke')
    
    if subcommand == 'create':
        _create_lug(manager, args[1:])
    elif subcommand == 'list':
        _list_lugs(manager, args[1:])
    elif subcommand == 'show':
        _show_lug(manager, args[1:])
    elif subcommand == 'update':
        _update_lug(manager, args[1:])
    elif subcommand == 'close':
        _close_lug(manager, args[1:])
    else:
        print_error(f"Unknown lug command: {subcommand}")
        _print_lug_help()
        sys.exit(1)


def _print_lug_help():
    """Print Lug command help."""
    print_info("""
WAI Lug Commands - AI-first task & dependency graph

Usage:
  wai lug create <title>              Create new Lug
  wai lug list [--status=STATUS]      List Lugs (filter optional)
  wai lug show <id-prefix>            Show Lug details
  wai lug update <id-prefix> [opts]   Update Lug fields
  wai lug close <id-prefix>           Close and archive Lug

Examples:
  wai lug create "Fix login bug"
  wai lug list --status=open --type=bug
  wai lug show a3f2
  wai lug update a3f2 --status=in_progress
  wai lug close a3f2
    """)


def _create_lug(manager: LugManager, args: list):
    """Create a new Lug interactively."""
    if not args:
        print_error("Usage: wai lug create <title>")
        sys.exit(1)
    
    title = ' '.join(args)
    
    print_info(f"\n📝 Creating Lug: {title}\n")
    
    # Prompt for type
    print_info("Type options: epic, issue, bug, work, ask (or custom)")
    lug_type = input("  Type [work]: ").strip() or 'work'
    
    # Prompt for priority
    print_info("Priority options: low, medium, high")
    priority = input("  Priority [medium]: ").strip() or 'medium'
    
    # Prompt for impact
    print_info("Impact options: small, medium, large")
    impact = input("  Impact [medium]: ").strip() or 'medium'
    
    # Prompt for value
    print_info("Value: 1-10 (ROI score)")
    value_input = input("  Value [5]: ").strip()
    value = int(value_input) if value_input else 5
    
    # Optional justification
    print_info("Justification (optional, press Enter to skip):")
    justification = input("  > ").strip() or None
    
    # Optional origin
    print_info("Origin (optional, e.g., 'user_request:chat', press Enter to skip):")
    origin = input("  > ").strip() or None
    
    # Create the Lug
    lug = manager.create_lug(
        title=title,
        lug_type=lug_type,
        priority=priority,
        impact=impact,
        value=value,
        justification=justification,
        origin=origin
    )
    
    print_success(f"\n✓ Created Lug: {lug.id}")
    print_info(f"  Title: {lug.title}")
    print_info(f"  Type: {lug.type}")
    print_info(f"  Priority: {lug.priority}")
    print_info(f"  Impact: {lug.impact}")
    print_info(f"  Value: {lug.value}")
    print_info(f"  Status: {lug.status}\n")
    
    # YOLO mode gating
    if priority == 'high' or impact == 'large' or value >= 7:
        print_warning("⚠️  High priority/impact/value detected!")
        print_info("YOLO mode: Consider reviewing before proceeding with implementation.\n")


def _list_lugs(manager: LugManager, args: list):
    """List Lugs with optional filters."""
    # Parse filters
    status_filter = None
    type_filter = None
    priority_filter = None
    
    for arg in args:
        if arg.startswith('--status='):
            status_filter = arg.split('=')[1]
        elif arg.startswith('--type='):
            type_filter = arg.split('=')[1]
        elif arg.startswith('--priority='):
            priority_filter = arg.split('=')[1]
    
    lugs = manager.list_lugs(status=status_filter, lug_type=type_filter, priority=priority_filter)
    
    if not lugs:
        print_info("No Lugs found.")
        return
    
    print_info(f"\n📋 Found {len(lugs)} Lug(s):\n")
    print_info(f"{'ID':<18} {'Type':<10} {'Priority':<10} {'Status':<12} {'Title':<50}")
    print_info("-" * 100)
    
    for lug in lugs:
        print_info(f"{lug.id:<18} {lug.type:<10} {lug.priority:<10} {lug.status:<12} {lug.title:<50}")
    
    print_info("")


def _show_lug(manager: LugManager, args: list):
    """Show detailed Lug information."""
    if not args:
        print_error("Usage: wai lug show <id-prefix>")
        sys.exit(1)
    
    lug_id_prefix = args[0]
    
    try:
        lug = manager.get_lug(lug_id_prefix)
        if not lug:
            print_error(f"No Lug found with ID prefix: {lug_id_prefix}")
            sys.exit(1)
        
        print_info(f"\n📌 Lug: {lug.id}\n")
        print_info(f"  Title: {lug.title}")
        print_info(f"  Type: {lug.type}")
        print_info(f"  Status: {lug.status}")
        print_info(f"  Priority: {lug.priority}")
        print_info(f"  Impact: {lug.impact}")
        print_info(f"  Value: {lug.value}")
        print_info(f"  Created: {lug.created_at}")
        print_info(f"  Updated: {lug.updated_at}")
        
        if lug.closed_at:
            print_info(f"  Closed: {lug.closed_at}")
        
        if lug.deps:
            print_info(f"  Dependencies: {', '.join(lug.deps)}")
        
        if lug.blocked_by:
            print_info(f"  Blocked by: {', '.join(lug.blocked_by)}")
        
        if lug.policy_tags:
            print_info(f"  Policy tags: {', '.join(lug.policy_tags)}")
        
        if lug.justification:
            print_info(f"  Justification: {lug.justification}")
        
        if lug.origin:
            print_info(f"  Origin: {lug.origin}")
        
        if lug.from_file:
            print_info(f"  From file: {lug.from_file}")
        
        if lug.summary:
            print_info(f"  Summary: {lug.summary}")
        
        if lug.resolved_by:
            print_info(f"  Resolved by: {lug.resolved_by}")
        
        if lug.extras:
            print_info(f"  Extras: {lug.extras}")
        
        print_info("")
        
    except ValueError as e:
        print_error(str(e))
        sys.exit(1)


def _update_lug(manager: LugManager, args: list):
    """Update an existing Lug."""
    if not args:
        print_error("Usage: wai lug update <id-prefix> [--status=STATUS] [--priority=PRIORITY] ...")
        sys.exit(1)
    
    lug_id_prefix = args[0]
    
    # Parse updates
    status = None
    priority = None
    impact = None
    value = None
    
    for arg in args[1:]:
        if arg.startswith('--status='):
            status = arg.split('=')[1]
        elif arg.startswith('--priority='):
            priority = arg.split('=')[1]
        elif arg.startswith('--impact='):
            impact = arg.split('=')[1]
        elif arg.startswith('--value='):
            value = int(arg.split('=')[1])
    
    if not any([status, priority, impact, value]):
        print_error("No updates specified. Use --status, --priority, --impact, or --value.")
        sys.exit(1)
    
    try:
        lug = manager.update_lug(
            lug_id_prefix=lug_id_prefix,
            status=status,
            priority=priority,
            impact=impact,
            value=value
        )
        
        print_success(f"✓ Updated Lug: {lug.id}")
        print_info(f"  Status: {lug.status}")
        print_info(f"  Priority: {lug.priority}")
        print_info(f"  Impact: {lug.impact}")
        print_info(f"  Value: {lug.value}\n")
        
    except ValueError as e:
        print_error(str(e))
        sys.exit(1)


def _close_lug(manager: LugManager, args: list):
    """Close and archive a Lug."""
    if not args:
        print_error("Usage: wai lug close <id-prefix>")
        sys.exit(1)
    
    lug_id_prefix = args[0]
    
    try:
        lug = manager.get_lug(lug_id_prefix)
        if not lug:
            print_error(f"No Lug found with ID prefix: {lug_id_prefix}")
            sys.exit(1)
        
        print_info(f"\n🔒 Closing Lug: {lug.id}")
        print_info(f"  Title: {lug.title}\n")
        
        # Optional summary
        print_info("Summary (optional, press Enter to skip):")
        summary = input("  > ").strip() or None
        
        # Check policies
        violations = manager.validate_policies(lug)
        if violations:
            print_warning("⚠️  Policy violations detected:")
            for violation in violations:
                print_warning(f"    - {violation}")
            
            if not safe_confirm("\nClose anyway?", default=False):
                print_info("Cancelled.")
                return
        
        # Close the Lug
        closed_lug = manager.close_lug(
            lug_id_prefix=lug_id_prefix,
            summary=summary,
            skip_policy_check=bool(violations)  # Skip check if user confirmed
        )
        
        print_success(f"\n✓ Closed Lug: {closed_lug.id}")
        print_info(f"  Archived to: lugs-closed.jsonl\n")
        
    except ValueError as e:
        print_error(str(e))
        sys.exit(1)
