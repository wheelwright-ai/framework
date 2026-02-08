"""
Session Briefing - Generate context about observations and work in progress.

Provides AI with complete session lookback including observation playback.
"""

from typing import Dict, Any, List, Optional
from wai.observation import get_logger
from datetime import datetime, timezone


class SessionBriefing:
    """Generate briefing with observation playback."""

    def __init__(self):
        """Initialize briefing generator."""
        self.logger = get_logger()

    def get_recent_observations(self, count: int = 10) -> List[Dict[str, Any]]:
        """Get recent observations for briefing."""
        return self.logger.get_recent_observations(count)

    def get_failed_observations(self) -> List[Dict[str, Any]]:
        """Get failed observations requiring attention."""
        return self.logger.get_failed_observations()

    def build_observation_summary(self) -> Dict[str, Any]:
        """Build summary of all observations."""
        all_obs = self.logger._read_all()
        
        if not all_obs:
            return {
                "total": 0,
                "summary": "No observations yet",
                "breakdown": {
                    "complete": 0,
                    "failed": 0,
                },
            }
        
        complete = sum(1 for obs in all_obs if obs["status"] == "complete")
        failed = sum(1 for obs in all_obs if obs["status"] == "failed")
        
        # Group by action category
        categories = {}
        for obs in all_obs:
            cat = obs["action"]["category"]
            if cat not in categories:
                categories[cat] = {"count": 0, "passed": 0, "failed": 0}
            categories[cat]["count"] += 1
            if obs["status"] == "complete":
                categories[cat]["passed"] += 1
            else:
                categories[cat]["failed"] += 1
        
        return {
            "total": len(all_obs),
            "complete": complete,
            "failed": failed,
            "categories": categories,
            "summary": f"{complete}/{len(all_obs)} actions verified",
        }

    def playback_observations(self, session_id: Optional[str] = None) -> str:
        """
        Generate human-readable playback of observations.
        
        Args:
            session_id: Specific session to playback, or None for all
        
        Returns:
            Markdown-formatted observation playback
        """
        if session_id:
            obs_list = self.logger.get_observations_for_session(session_id)
        else:
            obs_list = self.logger.get_recent_observations(20)
        
        if not obs_list:
            return "No observations to playback"
        
        lines = ["# Session Observation Playback\n"]
        
        # Group by session
        by_session = {}
        for obs in obs_list:
            sid = obs["session_id"]
            if sid not in by_session:
                by_session[sid] = []
            by_session[sid].append(obs)
        
        for sid in sorted(by_session.keys(), reverse=True):
            obs_in_session = by_session[sid]
            passed = sum(1 for o in obs_in_session if o["status"] == "complete")
            failed = sum(1 for o in obs_in_session if o["status"] == "failed")
            
            lines.append(f"## Session: {sid}")
            lines.append(f"**Status:** {passed}/{len(obs_in_session)} passed")
            lines.append("")
            
            for obs in obs_in_session:
                status_emoji = "✅" if obs["status"] == "complete" else "❌"
                action = obs["action"]["id"]
                desc = obs["action"]["description"]
                timestamp = obs["timestamp"][:19]  # YYYY-MM-DDTHH:MM:SS
                
                lines.append(f"{status_emoji} **{action}** — {desc}")
                lines.append(f"   - Time: {timestamp}")
                lines.append(f"   - Agent: {obs.get('agent', 'Unknown')}")
                lines.append(f"   - Command: `{obs['command']}`")
                
                if obs["status"] == "failed" and obs.get("remediation"):
                    rem = obs["remediation"]
                    lines.append(f"   - **Issue:** {rem.get('issue', 'Unknown')}")
                    lines.append(f"   - **Fix:** {rem.get('suggested_next_step', 'See details')}")
                
                lines.append("")
        
        return "\n".join(lines)

    def build_session_briefing(self, session_id: Optional[str] = None) -> str:
        """
        Build complete session briefing for AI context.
        
        Args:
            session_id: Specific session, or None for overall briefing
        
        Returns:
            Markdown-formatted briefing
        """
        lines = ["# Session Briefing\n"]
        
        # Overview
        summary = self.build_observation_summary()
        lines.append("## Observation Summary")
        lines.append(f"- **Total Actions:** {summary['total']}")
        lines.append(f"- **Verified:** {summary.get('complete', 0)}")
        lines.append(f"- **Failed:** {summary.get('failed', 0)}")
        lines.append("")
        
        # Breakdown by category
        if summary.get("categories"):
            lines.append("### By Category")
            for cat, stats in summary["categories"].items():
                lines.append(f"- **{cat}:** {stats['passed']}/{stats['count']} passed")
            lines.append("")
        
        # Failed observations requiring attention
        failed = self.get_failed_observations()
        if failed:
            lines.append("## ⚠️ Failed Observations (Action Required)")
            for obs in failed:
                action = obs["action"]["id"]
                lines.append(f"\n### {action}")
                lines.append(f"**Command:** `{obs['command']}`")
                
                if obs.get("remediation"):
                    rem = obs["remediation"]
                    lines.append(f"**Issue:** {rem.get('issue', 'Unknown')}")
                    lines.append(f"**Fix:** {rem.get('suggested_next_step', 'See logs')}")
                    
                    if rem.get("recovery_steps"):
                        lines.append("**Recovery Steps:**")
                        for step in rem["recovery_steps"]:
                            lines.append(f"- {step}")
            
            lines.append("")
        
        # Recent observations
        recent = self.get_recent_observations(5)
        if recent:
            lines.append("## Recent Actions")
            for obs in recent:
                status = "✅" if obs["status"] == "complete" else "❌"
                lines.append(f"- {status} {obs['action']['id']} at {obs['timestamp'][:19]}")
            lines.append("")
        
        return "\n".join(lines)


def get_briefing() -> SessionBriefing:
    """Get briefing generator."""
    return SessionBriefing()


def build_session_briefing(session_id: Optional[str] = None) -> str:
    """Convenience: build session briefing."""
    return get_briefing().build_session_briefing(session_id)


def playback_observations(session_id: Optional[str] = None) -> str:
    """Convenience: playback observations."""
    return get_briefing().playback_observations(session_id)
