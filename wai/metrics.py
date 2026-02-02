"""
Analytics and metrics tracking for Wheelwright sessions.

Tracks session metrics, token efficiency, time spent, and AI wins.
"""

import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, List, Optional


class MetricsTracker:
    """Tracks and analyzes session metrics."""

    def __init__(self, wai_spoke_dir: Path):
        """Initialize metrics tracker for a spoke directory."""
        self.wai_spoke_dir = wai_spoke_dir
        self.state_file = wai_spoke_dir / 'WAI-State.json'

    def record_session_end(self, session_data: Dict[str, Any]) -> None:
        """
        Record session completion metrics.

        Args:
            session_data: Dict with session info (id, tokens, duration, etc.)
        """
        state = self._load_state()

        # Initialize analytics if not exists
        if 'analytics' not in state:
            state['analytics'] = self._get_default_analytics()

        analytics = state['analytics']

        # Update session metrics
        analytics['sessions']['total_count'] += 1
        analytics['sessions']['total_turns'] += session_data.get('turns', 0)

        # Calculate duration
        if 'duration_seconds' in session_data:
            duration = session_data['duration_seconds']
            analytics['sessions']['total_duration_seconds'] += duration
            analytics['sessions']['avg_duration_seconds'] = (
                analytics['sessions']['total_duration_seconds'] /
                analytics['sessions']['total_count']
            )

        # Update token metrics
        tokens_used = session_data.get('tokens_estimate', 0)
        baseline = analytics.get('baseline_mode', {})
        baseline_enabled = baseline.get('enabled', False)

        if baseline_enabled:
            baseline['total_tokens_used'] = baseline.get('total_tokens_used', 0) + tokens_used
            baseline['total_sessions'] = baseline.get('total_sessions', 0) + 1
            analytics['baseline_mode'] = baseline
        else:
            analytics['token_efficiency']['total_tokens_used'] += tokens_used

        # Update time tracking
        if 'time_together_seconds' in session_data:
            analytics['time_tracking']['total_time_together_seconds'] += session_data['time_together_seconds']

        if 'time_ai_alone_seconds' in session_data:
            analytics['time_tracking']['total_time_ai_alone_seconds'] += session_data['time_ai_alone_seconds']

        # Update AI wins if provided
        if 'ai_wins' in session_data:
            for win in session_data['ai_wins']:
                analytics['ai_wins'].append({
                    'session_id': session_data.get('session_id'),
                    'timestamp': datetime.now().isoformat(),
                    'type': win.get('type'),
                    'description': win.get('description'),
                    'tokens_saved': win.get('tokens_saved', 0)
                })

        # Update last activity
        analytics['last_updated'] = datetime.now().isoformat()

        self._save_state(state)

    def calculate_token_savings(self) -> Dict[str, Any]:
        """
        Calculate token savings vs baseline.

        Returns:
            Dict with savings analysis
        """
        state = self._load_state()
        analytics = state.get('analytics', self._get_default_analytics())

        baseline = analytics.get('baseline_mode', {})
        current = analytics.get('token_efficiency', {})

        if not baseline.get('enabled') or baseline.get('total_tokens_used', 0) == 0:
            return {
                'has_baseline': False,
                'message': 'No baseline data available. Enable baseline mode to track savings.'
            }

        baseline_tokens = baseline['total_tokens_used']
        optimized_tokens = current['total_tokens_used']

        tokens_saved = baseline_tokens - optimized_tokens
        percent_saved = (tokens_saved / baseline_tokens) * 100 if baseline_tokens > 0 else 0

        return {
            'has_baseline': True,
            'baseline_tokens': baseline_tokens,
            'optimized_tokens': optimized_tokens,
            'tokens_saved': tokens_saved,
            'percent_saved': percent_saved,
            'meets_claim': percent_saved >= 50  # 50-80% claim
        }

    def get_session_stats(self) -> Dict[str, Any]:
        """
        Get comprehensive session statistics.

        Returns:
            Dict with formatted stats
        """
        state = self._load_state()
        analytics = state.get('analytics', self._get_default_analytics())

        sessions = analytics['sessions']
        token_eff = analytics['token_efficiency']
        time_track = analytics['time_tracking']
        ai_wins = analytics.get('ai_wins', [])

        # Calculate averages
        avg_tokens_per_session = (
            token_eff['total_tokens_used'] / sessions['total_count']
            if sessions['total_count'] > 0 else 0
        )

        avg_turns_per_session = (
            sessions['total_turns'] / sessions['total_count']
            if sessions['total_count'] > 0 else 0
        )

        # Time calculations
        total_time_seconds = (
            time_track['total_time_together_seconds'] +
            time_track['total_time_ai_alone_seconds']
        )

        # Format durations
        def format_duration(seconds):
            if seconds < 60:
                return f"{int(seconds)}s"
            elif seconds < 3600:
                return f"{int(seconds / 60)}m {int(seconds % 60)}s"
            else:
                hours = int(seconds / 3600)
                minutes = int((seconds % 3600) / 60)
                return f"{hours}h {minutes}m"

        stats = {
            'sessions': {
                'total': sessions['total_count'],
                'total_turns': sessions['total_turns'],
                'avg_turns': round(avg_turns_per_session, 1),
                'avg_duration': format_duration(sessions.get('avg_duration_seconds', 0))
            },
            'tokens': {
                'total_used': token_eff['total_tokens_used'],
                'avg_per_session': int(avg_tokens_per_session),
                'context_limit': token_eff.get('context_limit', 200000)
            },
            'time': {
                'total': format_duration(total_time_seconds),
                'together': format_duration(time_track['total_time_together_seconds']),
                'ai_alone': format_duration(time_track['total_time_ai_alone_seconds']),
                'together_percent': (
                    time_track['total_time_together_seconds'] / total_time_seconds * 100
                    if total_time_seconds > 0 else 0
                )
            },
            'ai_wins': {
                'total': len(ai_wins),
                'recent': ai_wins[-5:] if ai_wins else []  # Last 5
            }
        }

        # Add token savings if available
        savings = self.calculate_token_savings()
        if savings.get('has_baseline'):
            stats['token_savings'] = {
                'baseline_tokens': savings['baseline_tokens'],
                'optimized_tokens': savings['optimized_tokens'],
                'tokens_saved': savings['tokens_saved'],
                'percent_saved': round(savings['percent_saved'], 1),
                'meets_claim': savings['meets_claim']
            }

        return stats

    def enable_baseline_mode(self) -> Dict[str, Any]:
        """
        Enable baseline mode tracking.

        Returns:
            Dict with confirmation
        """
        state = self._load_state()

        if 'analytics' not in state:
            state['analytics'] = self._get_default_analytics()

        state['analytics']['baseline_mode'] = {
            'enabled': True,
            'started_at': datetime.now().isoformat(),
            'total_tokens_used': 0,
            'total_sessions': 0,
            'description': 'Baseline capture: avoid Wheelwright optimizations; closeout still records session metrics'
        }

        self._save_state(state)

        return {
            'enabled': True,
            'message': 'Baseline mode enabled. Work without Wheelwright optimizations; run Closeout to record each session.'
        }

    def disable_baseline_mode(self) -> Dict[str, Any]:
        """
        Disable baseline mode and lock baseline data.

        Returns:
            Dict with baseline summary
        """
        state = self._load_state()
        analytics = state.get('analytics', {})
        baseline = analytics.get('baseline_mode', {})

        if not baseline.get('enabled'):
            return {
                'disabled': False,
                'message': 'Baseline mode was not enabled'
            }

        baseline['enabled'] = False
        baseline['ended_at'] = datetime.now().isoformat()

        self._save_state(state)

        return {
            'disabled': True,
            'baseline_tokens': baseline.get('total_tokens_used', 0),
            'baseline_sessions': baseline.get('total_sessions', 0),
            'message': 'Baseline mode disabled. Baseline data locked for comparison.'
        }

    def detect_ai_wins(self, conversation_log: List[Dict]) -> List[Dict[str, Any]]:
        """
        Detect AI wins from conversation log.

        Looks for:
        - Scope drift catches
        - Prevented rework
        - Early error detection
        - Complexity assessment that saved work

        Args:
            conversation_log: List of turn dicts from session log

        Returns:
            List of detected AI wins
        """
        wins = []

        # Keywords that indicate AI wins
        drift_keywords = ['scope drift', 'are you sure', 'this seems', 'out of scope']
        prevented_keywords = ['would have', 'prevented', 'caught', 'avoided']
        early_detection = ['before', 'early', 'upfront', 'planning']

        for turn in conversation_log:
            if turn.get('type') != 'assistant':
                continue

            content = turn.get('content', '').lower()

            # Detect scope drift catch
            if any(keyword in content for keyword in drift_keywords):
                wins.append({
                    'type': 'scope_drift_catch',
                    'description': 'AI detected and flagged scope drift before enabling',
                    'tokens_saved': 5000,  # Estimate
                    'timestamp': turn.get('timestamp')
                })

            # Detect prevented rework
            if any(keyword in content for keyword in prevented_keywords):
                wins.append({
                    'type': 'prevented_rework',
                    'description': 'AI prevented rework by catching issue early',
                    'tokens_saved': 3000,
                    'timestamp': turn.get('timestamp')
                })

            # Detect planning that saved work
            if 'plan accepted' in content or 'planning complete' in content:
                if any(keyword in content for keyword in early_detection):
                    wins.append({
                        'type': 'upfront_planning',
                        'description': 'Thorough planning prevented implementation issues',
                        'tokens_saved': 2000,
                        'timestamp': turn.get('timestamp')
                    })

        return wins

    def _get_default_analytics(self) -> Dict[str, Any]:
        """Get default analytics structure."""
        return {
            'sessions': {
                'total_count': 0,
                'total_turns': 0,
                'total_duration_seconds': 0,
                'avg_duration_seconds': 0
            },
            'token_efficiency': {
                'total_tokens_used': 0,
                'context_limit': 200000,
                'avg_tokens_per_session': 0
            },
            'time_tracking': {
                'total_time_together_seconds': 0,
                'total_time_ai_alone_seconds': 0
            },
            'baseline_mode': {
                'enabled': False,
                'total_tokens_used': 0,
                'total_sessions': 0
            },
            'ai_wins': [],
            'last_updated': datetime.now().isoformat()
        }

    def _load_state(self) -> Dict[str, Any]:
        """Load WAI-State.json."""
        with open(self.state_file, 'r') as f:
            return json.load(f)

    def _save_state(self, state: Dict[str, Any]) -> None:
        """Save WAI-State.json."""
        with open(self.state_file, 'w') as f:
            json.dump(state, f, indent=2)
