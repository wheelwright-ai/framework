"""
Session management for Wheelwright AI sessions.

Handles session lifecycle, conversation logging, and state tracking.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any, List
import hashlib


class SessionManager:
    """Manages AI session lifecycle and state."""

    def __init__(self, spoke_dir: Path):
        """Initialize session manager for a spoke directory."""
        self.spoke_dir = spoke_dir
        self.wai_spoke_dir = spoke_dir / 'WAI-Spoke'
        self.state_file = self.wai_spoke_dir / 'WAI-State.json'
        self.log_file = self.wai_spoke_dir / 'WAI-Session-Log.jsonl'
        self.signals_file = self.wai_spoke_dir / 'WAI-Signals.jsonl'

        # In-memory session state
        self.session_id: Optional[str] = None
        self.turn_count: int = 0
        self.started_at: Optional[datetime] = None
        self.tokens_estimate: int = 0

    def start_session(self, ai_name: str = "Claude Sonnet 4.5") -> Dict[str, Any]:
        """Start a new session."""
        self.session_id = self._generate_session_id()
        self.started_at = datetime.now()
        self.turn_count = 0
        self.tokens_estimate = 0

        # Update WAI-State.json
        state = self._load_state()
        state['_session_state']['current_session'] = {
            'session_id': self.session_id,
            'started_at': self.started_at.isoformat(),
            'ai_model': ai_name,
            'turns': 0
        }
        state['_session_state']['protocol_completed'] = False
        self._save_state(state)

        return {
            'session_id': self.session_id,
            'started_at': self.started_at.isoformat()
        }

    def log_turn(self, turn_type: str, content: str, metadata: Optional[Dict] = None) -> None:
        """Log a conversation turn to WAI-Session-Log.jsonl."""
        if not self.session_id:
            return  # No active session

        self.turn_count += 1

        # Estimate tokens (heuristic: ~4 chars per token)
        tokens = len(content) // 4
        self.tokens_estimate += tokens

        turn_data = {
            'timestamp': datetime.now().isoformat(),
            'turn': self.turn_count,
            'type': turn_type,  # 'user' or 'assistant'
            'content': content,
            'metadata': {
                'tokens_estimate': tokens,
                **(metadata or {})
            }
        }

        # Append to log file
        with open(self.log_file, 'a') as f:
            f.write(json.dumps(turn_data) + '\n')

    def get_capacity_estimate(self, context_limit: int = 200000) -> Dict[str, Any]:
        """
        Estimate current context capacity usage.

        Args:
            context_limit: Maximum context window size in tokens

        Returns:
            Dict with capacity info
        """
        # Load conversation log and sum tokens
        total_tokens = 0
        if self.log_file.exists():
            with open(self.log_file, 'r') as f:
                for line in f:
                    turn = json.loads(line)
                    total_tokens += turn.get('metadata', {}).get('tokens_estimate', 0)

        # Add estimate for system context (WAI files, code context, etc.)
        # Rough estimate: WAI files are ~10-15k tokens
        system_context_estimate = 15000
        total_tokens += system_context_estimate

        capacity_pct = total_tokens / context_limit

        return {
            'tokens_used': total_tokens,
            'context_limit': context_limit,
            'capacity_percent': capacity_pct,
            'capacity_display': f"{capacity_pct * 100:.1f}%",
            'warning_level': self._get_warning_level(capacity_pct)
        }

    def _get_warning_level(self, capacity_pct: float) -> str:
        """Determine warning level based on capacity."""
        if capacity_pct >= 0.90:
            return 'critical'
        elif capacity_pct >= 0.80:
            return 'high'
        elif capacity_pct >= 0.60:
            return 'medium'
        else:
            return 'normal'

    def extract_session_summary(self) -> Dict[str, Any]:
        """
        Extract summary from conversation log.

        Returns:
            Dict with session summary data
        """
        if not self.log_file.exists():
            return {
                'summary': 'No conversation log found',
                'key_topics': [],
                'files_modified': [],
                'turns': 0
            }

        turns = []
        with open(self.log_file, 'r') as f:
            for line in f:
                turns.append(json.loads(line))

        # Extract files mentioned
        files_modified = set()
        key_topics = set()

        for turn in turns:
            content = turn.get('content', '')

            # Simple file detection (look for .py, .md, .json, etc.)
            import re
            file_pattern = r'\b[\w/\-]+\.(py|md|json|jsonl|txt|sh)\b'
            files = re.findall(file_pattern, content)
            files_modified.update(files)

            # Extract topics from keywords (simplified)
            topic_keywords = ['implement', 'fix', 'add', 'update', 'create', 'remove', 'refactor']
            for keyword in topic_keywords:
                if keyword in content.lower():
                    key_topics.add(keyword)

        # Generate summary from last few assistant messages
        assistant_messages = [t for t in turns if t.get('type') == 'assistant']
        recent_work = []
        for msg in assistant_messages[-3:]:  # Last 3 assistant messages
            content = msg.get('content', '')
            # Extract first sentence
            first_sentence = content.split('.')[0]
            if len(first_sentence) < 200:
                recent_work.append(first_sentence)

        summary = ' '.join(recent_work) if recent_work else 'Session in progress'

        return {
            'summary': summary[:500],  # Limit to 500 chars
            'key_topics': sorted(list(key_topics))[:5],
            'files_modified': sorted(list(files_modified))[:10],
            'turns': len(turns)
        }

    def extract_high_impact_signals(self) -> List[Dict[str, Any]]:
        """
        Extract high-impact learnings from session.

        Scans conversation log for patterns that should be captured as signals.

        Returns:
            List of signal entries to append to WAI-Signals.jsonl
        """
        signals = []
        if not self.log_file.exists():
            return signals

        # Scan log for high-impact items
        import re
        
        # Pattern for explicit decisions: "DECISION: <decision> (Impact: <N>)"
        decision_pattern = re.compile(r'DECISION:\s*(.+?)\s*\(Impact:\s*(\d+)\)', re.IGNORECASE)

        with open(self.log_file, 'r') as f:
            for line in f:
                try:
                    turn = json.loads(line)
                    content = turn.get('content', '')
                    
                    # check for explicit pattern
                    match = decision_pattern.search(content)
                    if match:
                        decision_text = match.group(1)
                        impact = int(match.group(2))
                        
                        if impact >= 8:
                            signals.append({
                                "timestamp": turn.get('timestamp', datetime.now().isoformat()),
                                "by": turn.get('type', 'assistant'),
                                "offers": [{
                                    "type": "decision",
                                    "topic": decision_text[:50],  # Brief topic
                                    "impact": impact,
                                    "context": content[:200]
                                }],
                                "flags": {"extracted_from_log": True}
                            })
                            
                    # Check for metadata impact if present (structured logging)
                    meta = turn.get('metadata', {})
                    if meta.get('impact', 0) >= 8:
                        signals.append({
                            "timestamp": turn.get('timestamp', datetime.now().isoformat()),
                            "by": turn.get('type', 'assistant'),
                            "offers": [{
                                "type": meta.get('type', 'insight'),
                                "topic": meta.get('topic', 'High Impact Item'),
                                "impact": meta.get('impact'),
                                "context": content[:200]
                            }],
                             "flags": {"extracted_from_metadata": True}
                        })
                        
                except json.JSONDecodeError:
                    continue
                    
        return signals

    def clear_log(self) -> None:
        """Clear conversation log after successful closeout."""
        if self.log_file.exists():
            self.log_file.unlink()

    def _generate_session_id(self) -> str:
        """Generate unique session ID."""
        timestamp = datetime.now().isoformat()
        hash_input = f"{timestamp}{self.spoke_dir}"
        return hashlib.md5(hash_input.encode()).hexdigest()[:12]

    def _load_state(self) -> Dict[str, Any]:
        """Load WAI-State.json."""
        with open(self.state_file, 'r') as f:
            return json.load(f)

    def _save_state(self, state: Dict[str, Any]) -> None:
        """Save WAI-State.json."""
        with open(self.state_file, 'w') as f:
            json.dump(state, f, indent=2)
