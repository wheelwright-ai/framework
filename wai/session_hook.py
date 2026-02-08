"""
Session Hook - Integrate briefing into Claude context at session start.

This module provides the session start briefing that should be injected
into Claude's system prompt and AGENTS.md at the beginning of each session.
"""

from typing import Optional
from wai.briefing import build_session_briefing, get_briefing


def get_session_start_briefing(session_id: Optional[str] = None) -> str:
    """
    Generate session start briefing for Claude context.
    
    This should be displayed to the user and AI at session start to provide:
    1. Recent work summary
    2. Failed observations requiring remediation
    3. Incomplete items to continue
    
    Args:
        session_id: Specific session to brief on, or None for overall
    
    Returns:
        Markdown-formatted briefing for Claude context
    """
    briefing = get_briefing()
    
    # Build the briefing
    briefing_text = build_session_briefing(session_id)
    
    # Wrap with context marker for Claude
    wrapped = f"""
# Session Start Briefing

{briefing_text}

---

**What to do next:**
1. Review failed observations above (if any)
2. Address remediation steps if needed
3. Continue with your work
4. New observations will be logged automatically
"""
    
    return wrapped


def get_agents_md_session_focus(session_id: Optional[str] = None) -> str:
    """
    Generate updated "Session Focus" section for AGENTS.md.
    
    This should replace the "Session Focus" section in AGENTS.md
    dynamically at session start, showing the most recent work context.
    
    Args:
        session_id: Specific session to focus on, or None for overall
    
    Returns:
        Markdown-formatted "Session Focus" section for AGENTS.md
    """
    briefing = get_briefing()
    summary = briefing.build_observation_summary()
    failed = briefing.get_failed_observations()
    recent = briefing.get_recent_observations(3)
    
    lines = ["# Session Focus (Auto-Updated)\n"]
    
    # Overall stats
    lines.append("**System Status**")
    lines.append(f"- Total observations: {summary['total']}")
    lines.append(f"- Successful: {summary.get('complete', 0)}")
    lines.append(f"- Failed: {summary.get('failed', 0)}")
    lines.append("")
    
    # Recent work
    if recent:
        lines.append("**Recent Work**")
        for obs in recent:
            status = "✅" if obs["status"] == "complete" else "❌"
            lines.append(f"- {status} {obs['action']['id']}")
        lines.append("")
    
    # Failed observations needing attention
    if failed:
        lines.append("**⚠️ Action Required**")
        lines.append("")
        for obs in failed:
            lines.append(f"**{obs['action']['id']}**")
            if obs.get("remediation"):
                rem = obs["remediation"]
                lines.append(f"- Issue: {rem.get('issue', 'Unknown')}")
                lines.append(f"- Fix: {rem.get('suggested_next_step', 'See logs')}")
            lines.append("")
    else:
        lines.append("**✅ All Observations Clean**")
        lines.append("")
    
    lines.append("---\n")
    
    return "\n".join(lines)


def display_session_briefing(session_id: Optional[str] = None) -> None:
    """
    Display session briefing to console.
    
    Called at session start to show user context about recent work.
    
    Args:
        session_id: Optional specific session to show
    """
    briefing = get_session_start_briefing(session_id)
    print(briefing)


def export_agents_md_update(output_file: str = "AGENTS-FOCUS-UPDATE.md", session_id: Optional[str] = None) -> str:
    """
    Export AGENTS.md Session Focus update to file.
    
    This file can be used to manually update AGENTS.md or
    can be auto-integrated into the editing workflow.
    
    Args:
        output_file: File to write update to
        session_id: Optional session to focus on
    
    Returns:
        Path to written file
    """
    focus_md = get_agents_md_session_focus(session_id)
    
    with open(output_file, 'w') as f:
        f.write(focus_md)
    
    return output_file


# Session hook integration examples

def example_claude_system_prompt_injection():
    """
    Example of how to inject session briefing into Claude system prompt.
    
    This would be called at the start of a Claude conversation.
    """
    briefing = get_session_start_briefing()
    
    system_prompt = f"""You are Claude, helping with Wheelwright Framework development.

## Recent Context

{briefing}

## Your Role

Continue from where you left off, addressing any failed observations and maintaining the ongoing work.
"""
    
    return system_prompt


def example_agents_md_update():
    """
    Example of updating AGENTS.md with current session focus.
    
    In a real system, this would:
    1. Read AGENTS.md
    2. Find "Session Focus" section
    3. Replace with current focus from observations
    4. Write back to AGENTS.md
    """
    focus = get_agents_md_session_focus()
    
    # Would read AGENTS.md, find section, replace
    # agents_md_content = read_agents_md()
    # agents_md_content = replace_session_focus(agents_md_content, focus)
    # write_agents_md(agents_md_content)
    
    return focus
