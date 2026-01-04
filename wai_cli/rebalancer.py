"""
Content rebalancer for WAI-Spoke files.

Keeps WAI-State.json and WAI-State.md within token limits by intelligently
redistributing content between files.
"""

import json
from pathlib import Path
from typing import Dict, Any, List, Tuple


class FileRebalancer:
    """Rebalances content across WAI-Spoke files."""

    # Token limits (conservative to leave room for growth)
    JSON_TOKEN_LIMIT = 8000   # ~32KB at 4 chars/token
    MD_TOKEN_LIMIT = 12000    # ~48KB at 4 chars/token

    def __init__(self, wai_spoke_dir: Path):
        """Initialize rebalancer for a WAI-Spoke directory."""
        self.wai_spoke_dir = wai_spoke_dir
        self.state_json = wai_spoke_dir / 'WAI-State.json'
        self.state_md = wai_spoke_dir / 'WAI-State.md'
        self.guide_md = wai_spoke_dir / 'WAI-Guide.md'

    def check_balance(self) -> Dict[str, Any]:
        """
        Check current balance of files.

        Returns:
            Dict with size info and recommendations
        """
        result = {
            'json': self._check_file(self.state_json, self.JSON_TOKEN_LIMIT),
            'md': self._check_file(self.state_md, self.MD_TOKEN_LIMIT),
            'guide': self._check_file(self.guide_md, self.MD_TOKEN_LIMIT * 2),  # Guide can be larger
            'needs_rebalance': False,
            'recommendations': []
        }

        # Determine if rebalance needed
        if result['json']['exceeds_limit']:
            result['needs_rebalance'] = True
            result['recommendations'].append(
                f"WAI-State.json exceeds limit ({result['json']['tokens']} > {self.JSON_TOKEN_LIMIT}). "
                "Move historical decisions to WAI-State.md."
            )

        if result['md']['exceeds_limit']:
            result['needs_rebalance'] = True
            result['recommendations'].append(
                f"WAI-State.md exceeds limit ({result['md']['tokens']} > {self.MD_TOKEN_LIMIT}). "
                "Archive old content or move to WAI-Guide.md."
            )

        return result

    def rebalance(self) -> Dict[str, Any]:
        """
        Rebalance files to stay within limits.

        Returns:
            Dict with actions taken
        """
        balance_check = self.check_balance()

        if not balance_check['needs_rebalance']:
            return {
                'rebalanced': False,
                'reason': 'Files within limits'
            }

        actions = []

        # Rebalance JSON if needed
        if balance_check['json']['exceeds_limit']:
            json_actions = self._rebalance_json()
            actions.extend(json_actions)

        # Rebalance MD if needed
        if balance_check['md']['exceeds_limit']:
            md_actions = self._rebalance_md()
            actions.extend(md_actions)

        return {
            'rebalanced': True,
            'actions': actions
        }

    def _rebalance_json(self) -> List[str]:
        """
        Rebalance WAI-State.json by moving content to MD.

        Strategy:
        1. Move old decisions (keep recent 10, archive rest to MD)
        2. Move completed features to MD
        3. Move old bugs to MD
        4. Compress evolution_log (keep recent 5 entries)
        """
        actions = []

        with open(self.state_json, 'r') as f:
            state = json.load(f)

        # Archive old decisions
        decisions = state.get('decisions', [])
        if len(decisions) > 10:
            recent_decisions = decisions[-10:]
            old_decisions = decisions[:-10]

            state['decisions'] = recent_decisions
            self._archive_to_md('decisions', old_decisions)
            actions.append(f"Archived {len(old_decisions)} old decisions to WAI-State.md")

        # Archive completed features
        features = state.get('features', [])
        completed_features = [f for f in features if f.get('status') == 'completed']
        active_features = [f for f in features if f.get('status') != 'completed']

        if completed_features:
            state['features'] = active_features
            self._archive_to_md('features', completed_features)
            actions.append(f"Archived {len(completed_features)} completed features to WAI-State.md")

        # Archive resolved bugs
        bugs = state.get('bugs', [])
        resolved_bugs = [b for b in bugs if b.get('status') == 'resolved']
        active_bugs = [b for b in bugs if b.get('status') != 'resolved']

        if resolved_bugs:
            state['bugs'] = active_bugs
            self._archive_to_md('bugs', resolved_bugs)
            actions.append(f"Archived {len(resolved_bugs)} resolved bugs to WAI-State.md")

        # Trim evolution log
        evolution_log = state.get('_project_foundation', {}).get('evolution_log', [])
        if len(evolution_log) > 5:
            recent_evolutions = evolution_log[-5:]
            old_evolutions = evolution_log[:-5]

            state['_project_foundation']['evolution_log'] = recent_evolutions
            self._archive_to_md('evolution_log', old_evolutions)
            actions.append(f"Archived {len(old_evolutions)} old evolution entries to WAI-State.md")

        # Save updated JSON
        with open(self.state_json, 'w') as f:
            json.dump(state, f, indent=2)

        return actions

    def _rebalance_md(self) -> List[str]:
        """
        Rebalance WAI-State.md by archiving to WAI-Guide.md.

        Strategy:
        1. Move old archived content to bottom of WAI-Guide.md
        2. Keep recent strategic context in WAI-State.md
        """
        actions = []

        # For now, just truncate if too large
        # In future, implement smart archival
        md_content = self.state_md.read_text()
        tokens = len(md_content) // 4

        if tokens > self.MD_TOKEN_LIMIT:
            # Keep first 75% of content
            keep_chars = int(len(md_content) * 0.75)
            truncated = md_content[:keep_chars]
            truncated += "\n\n---\n\n*Content truncated - full history available in git*\n"

            self.state_md.write_text(truncated)
            actions.append(f"Truncated WAI-State.md (removed ~{tokens - (keep_chars // 4)} tokens)")

        return actions

    def _archive_to_md(self, section: str, items: List[Any]) -> None:
        """Append archived items to WAI-State.md."""
        md_content = self.state_md.read_text()

        # Add archive section if not exists
        archive_header = f"\n## Archived {section.title()}\n\n"

        if archive_header not in md_content:
            md_content += archive_header

        # Append items
        for item in items:
            if isinstance(item, dict):
                # Format dict as markdown
                md_content += f"- **{item.get('date', 'Unknown date')}**: {item.get('decision', item.get('description', str(item)))}\n"
            else:
                md_content += f"- {item}\n"

        self.state_md.write_text(md_content)

    def _check_file(self, filepath: Path, limit: int) -> Dict[str, Any]:
        """Check a single file against limit."""
        if not filepath.exists():
            return {
                'exists': False,
                'tokens': 0,
                'limit': limit,
                'exceeds_limit': False,
                'percent_used': 0.0
            }

        content = filepath.read_text()
        tokens = len(content) // 4  # Heuristic: 4 chars per token

        return {
            'exists': True,
            'tokens': tokens,
            'limit': limit,
            'exceeds_limit': tokens > limit,
            'percent_used': tokens / limit
        }

    def scan_unknown_files(self) -> List[Path]:
        """
        Scan WAI-Spoke/ for unknown files that need reconciliation.

        Returns:
            List of file paths that aren't standard WAI files
        """
        known_files = {
            'WAI-State.json',
            'WAI-State.md',
            'WAI-Guide.md',
            'WAI-Signals.jsonl',
            'WAI-KB-Sync.json',
            'WAI-Session-Log.jsonl',
            'WAI-Baseline-Log.jsonl',
            'WAI-Testing-Log.jsonl',
            'WAI-WebLLM-Instructions.md',
            'WAI-Backlog.md',
            'WAI-Implementation-Summary.md',
            'WAI-Hub-Learnings.md',  # Created by Teach, reconciled by Closeout
            'WAI-File-Index.json'  # File index for tracking modifications
        }

        known_dirs = {'hooks', 'seed', 'reference'}
        indexed_items = self._load_index_entries()

        unknown_files = []

        for item in self.wai_spoke_dir.iterdir():
            if item.is_file():
                if item.name not in known_files and item.name not in indexed_items:
                    unknown_files.append(item)
            elif item.is_dir():
                if item.name not in known_dirs and item.name not in indexed_items:
                    unknown_files.append(item)

        return unknown_files

    def _load_index_entries(self) -> set:
        index_path = self.wai_spoke_dir / 'WAI-File-Index.json'
        if not index_path.exists():
            return set()
        try:
            data = json.loads(index_path.read_text())
        except Exception:
            return set()

        entries = set()
        for section in ('core_files', 'operational_files', 'project_files', 'legacy_files'):
            items = data.get(section, {})
            if isinstance(items, dict):
                for key in items.keys():
                    entries.add(key)
                    entries.add(Path(key).name)
        return entries
