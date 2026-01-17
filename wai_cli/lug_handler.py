def _cmd_lug(self, args):
    """Handle lug command."""
    from .commands.lug import lug_command_group
    
    spoke_path = normalize_path(getattr(args, 'path', '.') or '.')
    
    # Pass lug_args to command group
    lug_args = getattr(args, 'lug_args', [])
    lug_command_group(lug_args, spoke_path)
