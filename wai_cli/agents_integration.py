"""
AGENTS.md Integration - Auto-updating project briefs for IDE context loading.

When IDE loads a project, it reads AGENTS.md (supported by Claude Code, Cursor, etc.)
This module keeps AGENTS.md in sync with latest WAI state on every closeout.

The AGENTS.md file serves as the "welcome message" on session start.
"""

import json
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional


class AgentsIntegration:
    """Manages AGENTS.md auto-update on closeout."""

    def __init__(self, spoke_dir: Path):
        """
        Initialize agents integration.
        
        Args:
            spoke_dir: Root of the project (not WAI-Spoke)
        """
        self.spoke_dir = spoke_dir
        self.wai_spoke_dir = spoke_dir / 'WAI-Spoke'
        self.agents_md = spoke_dir / 'AGENTS.md'

    def refresh_agents_md(self) -> bool:
        """
        Refresh AGENTS.md with latest state from WAI-State.json.
        
        Called during closeout to ensure next session starts with fresh, 
        topical context. Updates not just state values but the actual 
        Quick Start and Session Start Protocol sections to reflect 
        unfinished work, multi-stage items, and current priorities.
        
        Returns:
            True if refresh succeeded
        """
        if not self.agents_md.exists():
            # No AGENTS.md yet, project doesn't use this integration
            return False

        state_file = self.wai_spoke_dir / 'WAI-State.json'
        if not state_file.exists():
            return False

        try:
            # Load current state
            state = json.loads(state_file.read_text(encoding='utf-8'))
            
            # Read current AGENTS.md 
            current_content = self.agents_md.read_text(encoding='utf-8')
            
            # Extract and generate values
            project_name = self.spoke_dir.name
            timestamp = datetime.now().isoformat()
            
            # Current phase from context
            current_phase = state.get('context', {}).get('current_phase', 'In Progress')
            
            # Status from session state
            session_state = state.get('_session_state', {})
            protocol_complete = session_state.get('protocol_completed', False)
            status = 'Ready for next session' if protocol_complete else 'Active development'
            
            # Last closeout info
            last_closeout = session_state.get('last_closeout', {})
            last_summary = last_closeout.get('summary', 'No recent sessions')
            
            # Next actions from context - PRIORITIZE UNFINISHED WORK
            next_actions = state.get('context', {}).get('next_actions', [])
            
            # Build next actions with emphasis on incomplete items
            next_actions_text = self._build_topical_next_actions(next_actions, state)
            
            # Blockers from context
            blockers = state.get('context', {}).get('blockers', [])
            if blockers:
                blockers_text = '\n'.join([f'- {blocker}' for blocker in blockers])
            else:
                blockers_text = 'None'
            
            # Build last actions from most recent sessions
            last_actions_text = f"- {last_summary}"
            
            # Generate updated content - preserve structure, update values
            updated_content = current_content
            updated_content = updated_content.replace('{{PROJECT_NAME}}', project_name)
            updated_content = updated_content.replace('{{TIMESTAMP}}', timestamp)
            updated_content = updated_content.replace('{{CURRENT_PHASE}}', current_phase)
            updated_content = updated_content.replace('{{STATUS}}', status)
            updated_content = updated_content.replace('{{LAST_ACTIONS}}', last_actions_text)
            updated_content = updated_content.replace('{{NEXT_ACTIONS}}', next_actions_text)
            updated_content = updated_content.replace('{{BLOCKERS}}', blockers_text)
            
            # ENHANCED: Add session-specific topical briefing
            briefing_section = self._generate_topical_briefing(state, next_actions)
            if briefing_section:
               # Insert after Quick Start, before other sections
               if '## Quick Start' in updated_content:
                   # Find the end of Quick Start section (look for next ## heading)
                   pattern = r'(## Quick Start.*?\n(?:.*?\n)*?)(?=\n## )'
                   match = re.search(pattern, updated_content, re.DOTALL)
                   if match:
                       insertion_point = match.end(1)
                       updated_content = (
                           updated_content[:insertion_point] +
                           f'\n## Session Focus (Must Continue)\n\n{briefing_section}' +
                           updated_content[insertion_point:]
                       )
               else:
                   # Fallback: append at end
                   updated_content += f'\n\n## Session Focus (Must Continue)\n\n{briefing_section}'
            
            # Write updated AGENTS.md
            self.agents_md.write_text(updated_content, encoding='utf-8')
            
            return True
            
        except Exception as e:
            # Non-blocking - AGENTS.md update failure shouldn't stop closeout
            print(f"  [WARN] AGENTS.md refresh failed: {e}")
            return False

    def _build_topical_next_actions(self, next_actions: list, state: dict) -> str:
        """
        Build next actions list emphasizing multi-stage items and unfinished work.
        
        If an action was listed as "In Progress" or has sub-tasks remaining,
        surface those prominently.
        
        Args:
            next_actions: List of next actions
            state: Full WAI-State.json
            
        Returns:
            Formatted next actions with emphasis on continuations
        """
        if not next_actions:
            return '- Check WAI-State.json for detailed plan'
        
        # Build base actions
        actions_list = []
        for action in next_actions[:5]:
            # Check if this is a multi-stage item
            if any(word in str(action).lower() for word in ['stage', 'part', 'phase', 'step']):
                actions_list.append(f"**{action}** (MULTI-STAGE - CONTINUE)")
            else:
                actions_list.append(f"- {action}")
        
        # Add context about last session's incomplete work if available
        last_closeout = state.get('_session_state', {}).get('last_closeout', {})
        if last_closeout:
            last_actions = last_closeout.get('key_topics', [])
            if last_actions:
                actions_list.append("\n**Continuing from last session:**")
                for topic in last_actions[:3]:
                    actions_list.append(f"  - {topic}")
        
        return '\n'.join(actions_list)

    def _generate_topical_briefing(self, state: dict, next_actions: list) -> str:
        """
        Generate a topical briefing that emphasizes what MUST continue.
        
        This section surfaces:
        - Any incomplete multi-stage work
        - Items that were started but not finished
        - Critical blockers to resolve first
        - Dependencies that need to be respected
        
        Args:
            state: Full WAI-State.json
            next_actions: List of next actions
            
        Returns:
            Formatted briefing text (may be empty if no special focus needed)
        """
        briefing = []
        
        # Check for incomplete work from previous session
        last_closeout = state.get('_session_state', {}).get('last_closeout', {})
        if last_closeout:
            summary = last_closeout.get('summary', '').lower()
            
            # Look for partial completion indicators
            if any(word in summary for word in ['started', 'partial', 'incomplete', 'wip', 'in progress']):
                briefing.append("[INCOMPLETE] **WORK FROM LAST SESSION**")
                briefing.append(f"Summary: {last_closeout.get('summary', 'Check last session')}")
                briefing.append("")
        
        # Check for multi-stage items in next actions
        multi_stage = [a for a in next_actions if any(w in str(a).lower() for w in ['stage', 'phase', 'part', 'step'])]
        if multi_stage:
            briefing.append("[CONTINUE] **MULTI-STAGE ITEMS - IN SEQUENCE**")
            for item in multi_stage[:3]:
                briefing.append(f"- {item}")
            briefing.append("")
        
        # Highlight blockers
        blockers = state.get('context', {}).get('blockers', [])
        if blockers:
            briefing.append("[BLOCK] **BLOCKERS TO RESOLVE FIRST**")
            for blocker in blockers:
                briefing.append(f"- {blocker}")
            briefing.append("")
        
        return '\n'.join(briefing) if briefing else ""

    def generate_agents_md_from_template(self, template_path: Path) -> Optional[str]:
        """
        Generate fresh AGENTS.md from template with current state values.
        
        Used during init to create initial AGENTS.md.
        
        Args:
            template_path: Path to AGENTS.md template
            
        Returns:
            Generated content or None if template not found
        """
        if not template_path.exists():
            return None

        try:
            content = template_path.read_text(encoding='utf-8')
            
            # Load state if it exists
            state_file = self.wai_spoke_dir / 'WAI-State.json'
            project_name = self.spoke_dir.name
            timestamp = datetime.now().isoformat()
            
            if state_file.exists():
                state = json.loads(state_file.read_text(encoding='utf-8'))
                current_phase = state.get('context', {}).get('current_phase', 'Initialization')
            else:
                current_phase = 'Initialization'
            
            # Apply substitutions
            content = content.replace('{{PROJECT_NAME}}', project_name)
            content = content.replace('{{TIMESTAMP}}', timestamp)
            content = content.replace('{{CURRENT_PHASE}}', current_phase)
            content = content.replace('{{STATUS}}', 'Initializing wheel...')
            content = content.replace('{{LAST_ACTIONS}}', '- Project initialization')
            content = content.replace('{{NEXT_ACTIONS}}', '- Complete project foundation\n- Define scope and boundaries')
            content = content.replace('{{BLOCKERS}}', 'None - ready to start')
            
            return content
            
        except Exception as e:
            print(f"  [WARN] AGENTS.md generation failed: {e}")
            return None
