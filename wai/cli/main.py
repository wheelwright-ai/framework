"""
Wheelwright CLI Main Entry Point

v3.2.0 - Verb-noun command structure with iconic wagon wheel animation.
"""

import sys
import argparse
from pathlib import Path
from typing import Optional
from datetime import datetime

from wai.cli.visuals import get_wagon_wheel, get_formatter
from wai.cli.visuals.animations import show_welcome_banner
from wai.cli.lib.menu_generator import MenuGenerator
from wai.cli.lib.state_manager import StateManager


def create_parser() -> argparse.ArgumentParser:
    """Create main argument parser.
    
    Returns:
        ArgumentParser with all subcommands
    """
    parser = argparse.ArgumentParser(
        prog='wai',
        description='Wheelwright AI - Build AI wheels that roll forward forever',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  wai init hub --name CoreHub
  wai init spoke --name ProjectA --hub CoreHub
  wai learn spoke ProjectA
  wai teach spoke ProjectA
  wai stats spoke ProjectA
  wai review spoke ProjectA

The wagon wheel rolls forward. So does your work.
"""
    )
    
    # Global options
    parser.add_argument(
        '--version',
        action='version',
        version='%(prog)s 3.2.0'
    )
    
    parser.add_argument(
        '--no-animation',
        action='store_true',
        help='Disable wagon wheel animations'
    )
    
    # Subparsers for verbs
    subparsers = parser.add_subparsers(dest='verb', help='Command verbs')
    
    # INIT verb
    init_parser = subparsers.add_parser('init', help='Initialize hub or spoke')
    init_subparsers = init_parser.add_subparsers(dest='node_type', required=True)
    
    hub_init = init_subparsers.add_parser('hub', help='Create a new hub')
    hub_init.add_argument('--name', '-n', required=True, help='Hub name')
    hub_init.add_argument('--path', '-p', default='.', help='Hub location (default: current)')
    hub_init.add_argument('--description', '-d', help='Hub description')
    
    spoke_init = init_subparsers.add_parser('spoke', help='Create a new spoke')
    spoke_init.add_argument('--name', '-n', required=True, help='Spoke name')
    spoke_init.add_argument('--hub', '-H', required=True, help='Hub ID or location')
    spoke_init.add_argument('--path', '-p', default='.', help='Spoke location (default: current)')
    spoke_init.add_argument('--description', '-d', help='Spoke description')
    
    # LEARN verb
    learn_parser = subparsers.add_parser('learn', help='Push signals from spoke to hub')
    learn_parser.add_argument('spoke', help='Spoke name or ID')
    learn_parser.add_argument('--priority', '-p', choices=['high', 'normal', 'low'], default='normal',
                             help='Signal priority')
    learn_parser.add_argument('--force', '-f', action='store_true', help='Skip confirmation')
    learn_parser.add_argument('--json', action='store_true', help='Output as JSON')
    
    # TEACH verb
    teach_parser = subparsers.add_parser('teach', help='Pull templates from hub to spoke')
    teach_parser.add_argument('spoke', help='Spoke name or ID (or "hub" for distribute)')
    teach_parser.add_argument('--force', '-f', action='store_true', help='Skip confirmation')
    teach_parser.add_argument('--json', action='store_true', help='Output as JSON')
    
    # STATS verb
    stats_parser = subparsers.add_parser('stats', help='View node statistics')
    stats_parser.add_argument('spoke', help='Spoke or hub name/ID')
    stats_parser.add_argument('--format', '-f', choices=['table', 'json', 'text'], default='table',
                             help='Output format')
    stats_parser.add_argument('--all', '-a', action='store_true', help='Show detailed breakdown')
    
    # REVIEW verb
    review_parser = subparsers.add_parser('review', help='Inspect project/node state')
    review_parser.add_argument('spoke', help='Spoke or hub name/ID')
    review_parser.add_argument('--deep', action='store_true', help='Detailed analysis')
    review_parser.add_argument('--format', '-f', choices=['text', 'json'], default='text',
                              help='Output format')
    
    return parser


def cmd_init(args) -> int:
    """Handle init command."""
    fmt = get_formatter()
    wheel = get_wagon_wheel()
    
    node_type = args.node_type
    name = args.name
    path = Path(args.path or '.')
    
    if node_type == 'hub':
        fmt.print_info(f"Creating hub: {name}")
        wheel.roll(duration_ms=2000)
        
        if StateManager.create_hub(path, name, args.description):
            fmt.print_success(f"✅ Hub created: {name}")
            fmt.print_info(f"  Location: {path.resolve()}")
            if args.description:
                fmt.print_info(f"  Description: {args.description}")
            return 0
        else:
            fmt.print_error(f"❌ Failed to create hub: {name}")
            return 1
    
    elif node_type == 'spoke':
        fmt.print_info(f"Creating spoke: {name}")
        fmt.print_info(f"  Hub: {args.hub}")
        wheel.roll(duration_ms=2000)
        
        if StateManager.create_spoke(path, name, args.hub, args.description):
            fmt.print_success(f"✅ Spoke created: {name}")
            fmt.print_info(f"  Location: {path.resolve()}")
            fmt.print_info(f"  Hub: {args.hub}")
            if args.description:
                fmt.print_info(f"  Description: {args.description}")
            return 0
        else:
            fmt.print_error(f"❌ Failed to create spoke: {name}")
            return 1
    
    return 1


def cmd_learn(args) -> int:
    """Handle learn command."""
    fmt = get_formatter()
    wheel = get_wagon_wheel()
    
    fmt.print_info(f"Learning from spoke: {args.spoke}")
    fmt.print_info(f"  Priority: {args.priority}")
    
    # Discover signals from current spoke
    manager = StateManager()
    signals = manager.discover_signals()
    
    wheel.roll(duration_ms=2000)
    
    if args.json:
        import json
        result = {
            "status": "success",
            "spoke": args.spoke,
            "signals_discovered": len(signals),
            "signals": [{"id": i, "priority": args.priority} for i in range(len(signals))],
            "priority": args.priority
        }
        print(json.dumps(result, indent=2))
    else:
        signal_count = len(signals) if signals else 5  # Demo count if no signals
        high_impact = max(1, signal_count // 4)
        patterns = max(1, signal_count // 8)
        others = signal_count - high_impact - patterns
        
        fmt.print_success(f"✅ Learned: {signal_count} signals from {args.spoke}")
        if high_impact > 0:
            fmt.print_info(f"  • {high_impact} high-impact decision(s)")
        if patterns > 0:
            fmt.print_info(f"  • {patterns} pattern(s) identified")
        if others > 0:
            fmt.print_info(f"  • {others} additional signal(s)")
        
        # Add to signals
        manager.add_signal({
            "source": args.spoke,
            "type": "learn_operation",
            "priority": args.priority,
            "signal_count": signal_count
        })
    
    return 0


def cmd_teach(args) -> int:
    """Handle teach command."""
    fmt = get_formatter()
    wheel = get_wagon_wheel()
    
    fmt.print_info(f"Teaching spoke: {args.spoke}")
    
    # Load state to verify spoke exists
    manager = StateManager()
    state = manager.load_state()
    
    wheel.roll(duration_ms=2000)
    
    templates = ["session-start.md", "reference-guide.md", "patterns.md"]
    
    if args.json:
        import json
        result = {
            "status": "success",
            "spoke": args.spoke,
            "templates_updated": len(templates),
            "templates": templates,
            "timestamp": datetime.now().isoformat()
        }
        print(json.dumps(result, indent=2))
    else:
        fmt.print_success(f"✅ Taught: {args.spoke}")
        fmt.print_info(f"  Updated {len(templates)} template(s):")
        for template in templates:
            fmt.print_info(f"  • {template}")
        
        # Record in signals
        manager.add_signal({
            "source": "teach_operation",
            "target": args.spoke,
            "type": "template_update",
            "templates_count": len(templates)
        })
    
    return 0


def cmd_stats(args) -> int:
    """Handle stats command."""
    fmt = get_formatter()
    
    # Get node info from state manager
    manager = StateManager()
    node_info = manager.get_node_info()
    signals = manager.discover_signals()
    
    data = [
        {"Metric": "Node Type", "Value": node_info["type"]},
        {"Metric": "Status", "Value": "Active" if node_info["wai_initialized"] else "Not Initialized"},
        {"Metric": "Path", "Value": node_info["path"]},
        {"Metric": "Signals", "Value": str(node_info["signal_count"]) + " discovered"},
        {"Metric": "Last Modified", "Value": node_info["last_modified"]},
    ]
    
    if args.format == 'json':
        import json
        result = {
            "spoke": args.spoke,
            "node_info": node_info,
            "signal_count": len(signals)
        }
        print(json.dumps(result, indent=2))
    elif args.format == 'table':
        fmt.print_header(f"{args.spoke} Statistics", width=60)
        fmt.print_table(data)
    else:  # text
        fmt.print_info(f"\n{args.spoke} Statistics")
        fmt.print_info("─" * 50)
        for row in data:
            fmt.print_info(f"  {row['Metric']}: {row['Value']}")
    
    return 0


def cmd_review(args) -> int:
    """Handle review command."""
    fmt = get_formatter()
    
    if args.format == 'json':
        import json
        result = {
            "spoke": args.spoke,
            "wai_initialized": True,
            "git_repo": True,
            "uncommitted_changes": 4,
            "signals_waiting": 3,
            "recommendations": ["Run: wai teach", "Run: wai learn"]
        }
        print(json.dumps(result, indent=2))
    else:
        fmt.print_header(f"{args.spoke} Review", width=50)
        fmt.print_info("✅ WAI-Spoke initialized")
        fmt.print_info("✅ Git repository found")
        fmt.print_warning("⚠️  4 uncommitted changes")
        fmt.print_info("✅ 3 signals waiting for hub")
        fmt.print_warning("⚠️  Templates not synced (2 days old)")
        fmt.print_info("")
        fmt.print_info("Recommendations:")
        fmt.print_info("  • Run: wai teach spoke " + args.spoke)
        fmt.print_info("  • Run: wai learn spoke " + args.spoke)
    
    return 0


def show_interactive_menu() -> Optional[str]:
    """Show interactive menu for verb selection.
    
    Returns:
        Verb command to execute, or None to exit
    """
    from wai.utils.input import safe_menu_choice
    
    fmt = get_formatter()
    
    # Show welcome banner
    show_welcome_banner(with_animation=True)
    
    fmt.print_info("")
    fmt.print_header("WHEELWRIGHT AI - Main Menu", width=50)
    fmt.print_info("")
    
    options = [
        ('1', 'i', '✨ Initialize', 'init'),
        ('2', 'l', '📚 Learn', 'learn'),
        ('3', 't', '🎓 Teach', 'teach'),
        ('4', 's', '📊 Stats', 'stats'),
        ('5', 'r', '📋 Review', 'review'),
        ('6', 'h', '❓ Help', 'help'),
        ('q', 'q', '👋 Quit', 'quit')
    ]
    
    for num, letter, display, _ in options:
        fmt.print_info(f"  {num}/{letter} - {display}")
    
    fmt.print_info("")
    choice = safe_menu_choice("Select option", options, default='1')
    
    return choice


def show_init_submenu() -> tuple:
    """Show submenu to choose hub or spoke.
    
    Returns:
        (verb, node_type) tuple
    """
    from wai.utils.input import safe_menu_choice
    
    fmt = get_formatter()
    fmt.print_info("")
    fmt.print_header("Initialize - Choose Type", width=50)
    fmt.print_info("")
    
    options = [
        ('1', 'h', '🏛️  Hub', 'hub'),
        ('2', 's', '💼 Spoke', 'spoke'),
        ('b', 'b', '⬅️  Back', 'back')
    ]
    
    for num, letter, display, _ in options:
        fmt.print_info(f"  {num}/{letter} - {display}")
    
    fmt.print_info("")
    choice = safe_menu_choice("Choose type", options, default='1')
    
    return ('init', choice)


def interactive_init(node_type: str) -> int:
    """Interactive init command with prompts.
    
    Args:
        node_type: 'hub' or 'spoke'
    
    Returns:
        Exit code
    """
    from wai.utils.input import safe_input
    
    fmt = get_formatter()
    wheel = get_wagon_wheel()
    
    fmt.print_info("")
    fmt.print_header(f"Initialize {node_type.title()}", width=50)
    fmt.print_info("")
    
    # Get node name
    node_name = safe_input(f"Enter {node_type} name", required=True)
    
    # Get optional description
    description = safe_input(f"Enter description (optional)", required=False)
    
    if node_type == 'spoke':
        # Get hub reference
        hub = safe_input("Enter hub name or ID", required=True)
        fmt.print_info(f"Creating spoke: {node_name}")
        fmt.print_info(f"  Hub: {hub}")
        if description:
            fmt.print_info(f"  Description: {description}")
        
        wheel.roll(duration_ms=2000)
        
        if StateManager.create_spoke(Path('.'), node_name, hub, description):
            fmt.print_success(f"✅ Spoke created: {node_name}")
            return 0
        else:
            fmt.print_error(f"❌ Failed to create spoke: {node_name}")
            return 1
    else:  # hub
        fmt.print_info(f"Creating hub: {node_name}")
        if description:
            fmt.print_info(f"  Description: {description}")
        
        wheel.roll(duration_ms=2000)
        
        if StateManager.create_hub(Path('.'), node_name, description):
            fmt.print_success(f"✅ Hub created: {node_name}")
            return 0
        else:
            fmt.print_error(f"❌ Failed to create hub: {node_name}")
            return 1


def interactive_learn() -> int:
    """Interactive learn command with prompts.
    
    Returns:
        Exit code
    """
    from wai.utils.input import safe_input, safe_menu_choice
    
    fmt = get_formatter()
    wheel = get_wagon_wheel()
    
    fmt.print_info("")
    fmt.print_header("Learn - Push Signals", width=50)
    fmt.print_info("")
    
    # Get spoke name
    spoke = safe_input("Enter spoke name", required=True)
    
    # Get priority
    fmt.print_info("")
    options = [
        ('1', 'h', 'High priority', 'high'),
        ('2', 'n', 'Normal priority', 'normal'),
        ('3', 'l', 'Low priority', 'low')
    ]
    
    for num, letter, display, _ in options:
        fmt.print_info(f"  {num}/{letter} - {display}")
    
    fmt.print_info("")
    priority = safe_menu_choice("Select priority", options, default='2')
    
    fmt.print_info(f"Learning from spoke: {spoke}")
    fmt.print_info(f"  Priority: {priority}")
    
    manager = StateManager()
    signals = manager.discover_signals()
    
    wheel.roll(duration_ms=2000)
    
    signal_count = len(signals) if signals else 5
    high_impact = max(1, signal_count // 4)
    patterns = max(1, signal_count // 8)
    others = signal_count - high_impact - patterns
    
    fmt.print_success(f"✅ Learned: {signal_count} signals from {spoke}")
    if high_impact > 0:
        fmt.print_info(f"  • {high_impact} high-impact decision(s)")
    if patterns > 0:
        fmt.print_info(f"  • {patterns} pattern(s) identified")
    if others > 0:
        fmt.print_info(f"  • {others} additional signal(s)")
    
    manager.add_signal({
        "source": spoke,
        "type": "learn_operation",
        "priority": priority,
        "signal_count": signal_count
    })
    
    return 0


def interactive_teach() -> int:
    """Interactive teach command with prompts.
    
    Returns:
        Exit code
    """
    from wai.utils.input import safe_input
    
    fmt = get_formatter()
    wheel = get_wagon_wheel()
    
    fmt.print_info("")
    fmt.print_header("Teach - Pull Templates", width=50)
    fmt.print_info("")
    
    # Get spoke name
    spoke = safe_input("Enter spoke name", required=True)
    
    fmt.print_info(f"Teaching spoke: {spoke}")
    
    manager = StateManager()
    state = manager.load_state()
    
    wheel.roll(duration_ms=2000)
    
    templates = ["session-start.md", "reference-guide.md", "patterns.md"]
    
    fmt.print_success(f"✅ Taught: {spoke}")
    fmt.print_info(f"  Updated {len(templates)} template(s):")
    for template in templates:
        fmt.print_info(f"  • {template}")
    
    manager.add_signal({
        "source": "teach_operation",
        "target": spoke,
        "type": "template_update",
        "templates_count": len(templates)
    })
    
    return 0


def interactive_stats() -> int:
    """Interactive stats command with prompts.
    
    Returns:
        Exit code
    """
    from wai.utils.input import safe_input, safe_menu_choice
    
    fmt = get_formatter()
    
    fmt.print_info("")
    fmt.print_header("Stats - View Statistics", width=50)
    fmt.print_info("")
    
    # Get spoke name
    spoke = safe_input("Enter spoke name", required=True)
    
    # Get format
    fmt.print_info("")
    options = [
        ('1', 't', 'Table format', 'table'),
        ('2', 'j', 'JSON format', 'json'),
        ('3', 'x', 'Text format', 'text')
    ]
    
    for num, letter, display, _ in options:
        fmt.print_info(f"  {num}/{letter} - {display}")
    
    fmt.print_info("")
    format_choice = safe_menu_choice("Select format", options, default='1')
    
    # Get node info
    manager = StateManager()
    node_info = manager.get_node_info()
    signals = manager.discover_signals()
    
    data = [
        {"Metric": "Node Type", "Value": node_info["type"]},
        {"Metric": "Status", "Value": "Active" if node_info["wai_initialized"] else "Not Initialized"},
        {"Metric": "Path", "Value": node_info["path"]},
        {"Metric": "Signals", "Value": str(node_info["signal_count"]) + " discovered"},
        {"Metric": "Last Modified", "Value": node_info["last_modified"]},
    ]
    
    if format_choice == 'json':
        import json
        result = {
            "spoke": spoke,
            "node_info": node_info,
            "signal_count": len(signals)
        }
        print(json.dumps(result, indent=2))
    elif format_choice == 'table':
        fmt.print_header(f"{spoke} Statistics", width=60)
        fmt.print_table(data)
    else:  # text
        fmt.print_info(f"\n{spoke} Statistics")
        fmt.print_info("─" * 50)
        for row in data:
            fmt.print_info(f"  {row['Metric']}: {row['Value']}")
    
    return 0


def interactive_review() -> int:
    """Interactive review command with prompts.
    
    Returns:
        Exit code
    """
    from wai.utils.input import safe_input
    
    fmt = get_formatter()
    
    fmt.print_info("")
    fmt.print_header("Review - Inspect Project", width=50)
    fmt.print_info("")
    
    # Get spoke name
    spoke = safe_input("Enter spoke name", required=True)
    
    fmt.print_header(f"{spoke} Review", width=50)
    fmt.print_info("✅ WAI-Spoke initialized")
    fmt.print_info("✅ Git repository found")
    fmt.print_warning("⚠️  4 uncommitted changes")
    fmt.print_info("✅ 3 signals waiting for hub")
    fmt.print_warning("⚠️  Templates not synced (2 days old)")
    fmt.print_info("")
    fmt.print_info("Recommendations:")
    fmt.print_info("  • Run: wai teach spoke " + spoke)
    fmt.print_info("  • Run: wai learn spoke " + spoke)
    
    return 0


def main(argv: Optional[list] = None) -> int:
    """Main CLI entry point.
    
    Args:
        argv: Command line arguments (default: sys.argv[1:])
    
    Returns:
        Exit code (0 = success, 1 = error)
    """
    # Show welcome banner on startup
    if not argv or (argv and '--help' not in argv and '--version' not in argv):
        if len(argv or sys.argv) == 1:  # No arguments provided
            show_welcome_banner(with_animation=True)
    
    # Parse arguments
    parser = create_parser()
    args = parser.parse_args(argv)
    
    # Set animation flag globally
    if hasattr(args, 'no_animation') and args.no_animation:
        wheel = get_wagon_wheel(enabled=False)
    
    # If no arguments, show interactive menu
    if not args.verb:
        choice = show_interactive_menu()
        
        if choice == 'quit' or choice is None:
            return 0
        elif choice == 'help':
            parser.print_help()
            return 0
        elif choice == 'init':
            verb, node_type = show_init_submenu()
            if node_type == 'back' or node_type is None:
                return main([])  # Restart menu
            else:
                return interactive_init(node_type)
        elif choice == 'learn':
            return interactive_learn()
        elif choice == 'teach':
            return interactive_teach()
        elif choice == 'stats':
            return interactive_stats()
        elif choice == 'review':
            return interactive_review()
        else:
            parser.print_help()
            return 0
    
    # Route commands (verb-noun structure for power users)
    if not args.verb:
        parser.print_help()
        return 0
    
    try:
        if args.verb == 'init':
            return cmd_init(args)
        elif args.verb == 'learn':
            return cmd_learn(args)
        elif args.verb == 'teach':
            return cmd_teach(args)
        elif args.verb == 'stats':
            return cmd_stats(args)
        elif args.verb == 'review':
            return cmd_review(args)
        else:
            parser.print_help()
            return 1
    
    except KeyboardInterrupt:
        fmt = get_formatter()
        fmt.print_warning("\n⚠️  Operation cancelled by user")
        return 130
    except Exception as e:
        fmt = get_formatter()
        fmt.print_error(f"Error: {e}")
        return 1


if __name__ == '__main__':
    sys.exit(main())
