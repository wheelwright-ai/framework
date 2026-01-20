"""
wai ready command
=================

Lists Lugs that are ready to work on (unblocked, open), sorted by priority.
This is the primary "pull" mechanism for autonomous agents.
"""

import sys
import json
from pathlib import Path
from ..lugs import LugManager
from ..utils.input import print_info, print_error

def _colorize(text: str, color_code: str) -> str:
    COLOR_RESET = "\033[0m"
    return f"{color_code}{text}{COLOR_RESET}"

def _get_priority_color(priority: str) -> str:
    COLOR_RED = "\033[91m"
    COLOR_YELLOW = "\033[93m"
    COLOR_BLUE = "\033[94m"
    COLOR_RESET = "\033[0m"
    
    priority = str(priority).lower()
    if priority in ['0', 'critical', 'high', '1']: return COLOR_RED
    if priority in ['medium', '2']: return COLOR_YELLOW
    if priority in ['low', '3']: return COLOR_BLUE
    return COLOR_RESET

def ready_command(args: list, spoke_dir: Path):
    """
    Handle 'wai ready' command.
    Usage: wai ready [--limit=N] [--json]
    """
    manager = LugManager(spoke_dir / 'WAI-Spoke')
    
    # Parse args
    limit = 10
    json_output = False
    
    for arg in args:
        if arg.startswith('--limit='):
            try:
                limit = int(arg.split('=')[1])
            except ValueError:
                pass
        elif arg == '--json':
            json_output = True
    
    ready_lugs = manager.get_ready_lugs(limit=limit)
    
    if json_output:
        # Output JSONL for agents
        for lug in ready_lugs:
            print(json.dumps(lug.to_dict()))
        return
        
    # Human-readable table
    if not ready_lugs:
        print_info("No ready work found (all open lugs are blocked or backlog empty).")
        return
        
    print_info(f"\n🚀 Ready Work ({len(ready_lugs)} items, limit={limit}):\n")
    print_info(f"{'ID':<10} {'Pri':<8} {'Value':<6} {'Title'}")
    print_info("-" * 80)
    
    for lug in ready_lugs:
        title = (lug.title[:50] + '...') if len(lug.title) > 53 else lug.title
        prio_str = _colorize(f"{str(lug.priority)[:3]:<8}", _get_priority_color(lug.priority))
        
        print_info(f"{lug.id[:8]:<10} {prio_str} {str(lug.value):<6} {title}")
    
    print_info("")
