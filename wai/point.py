"""
WAI-Point.json - Minimal bootstrap file for quick context restoration.

Provides lightweight entry point with essentials:
- Project summary
- Open Lugs summary
- Last shipit timestamp
- Key learnings

Updated on shipit, can be ingested from seed/ingest/ during closeout.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional


class PointManager:
    """Manages WAI-Point.json bootstrap file."""
    
    def __init__(self, spoke_dir: Path):
        """Initialize PointManager with spoke directory."""
        self.spoke_dir = spoke_dir
        self.wai_spoke_dir = spoke_dir / 'WAI-Spoke'
        self.point_file = self.wai_spoke_dir / 'WAI-Point.json'
        self.state_file = self.wai_spoke_dir / 'WAI-State.json'
    
    def generate_point(self) -> Dict[str, Any]:
        """
        Generate WAI-Point from current state and Lugs.
        
        Returns:
            Point data dict
        """
        point = {
            'schema_version': 1,
            'generated_at': datetime.now().isoformat(),
            'project': {
                'name': 'Unknown',
                'version': '0.0.0'
            },
            'summary': '',
            'open_lugs': [],
            'open_lugs_summary': 'No Lugs system initialized',
            'next_session_lug': None,
            'last_shipit': None,
            'key_learnings': []
        }
        
        # Load state
        if self.state_file.exists():
            with open(self.state_file, 'r') as f:
                state = json.load(f)
            
            # Extract project summary
            project = state.get('project', {})
            wheel = state.get('wheel', {})
            hub = state.get('hub', {})
            point['project'] = {
                'name': project.get('name') or hub.get('name', 'Unknown'),
                'version': project.get('version') or state.get('framework', {}).get('version', '0.0.0')
            }
            point['summary'] = project.get('description') or wheel.get('description') or hub.get('summary', '')
            
            # Extract last shipit info
            session_state = state.get('_session_state', {})
            last_closeout = session_state.get('last_closeout', {})
            if last_closeout:
                point['last_shipit'] = {
                    'timestamp': last_closeout.get('closed_at'),
                    'summary': last_closeout.get('summary'),
                    'key_topics': last_closeout.get('key_topics', [])
                }
            
            # Extract key learnings from insights
            context = state.get('context', {})
            insights = context.get('insights', [])
            point['key_learnings'] = insights[:5]  # Top 5
        
        # Load open Lugs summary
        lugs_file = self.wai_spoke_dir / 'lugs.jsonl'
        if lugs_file.exists():
            open_lugs = []
            with open(lugs_file, 'r') as f:
                for line in f:
                    if line.strip():
                        try:
                            lug_data = json.loads(line)
                            # Expand minified keys if needed
                            from .lugs import MINIFIED_KEYS
                            expanded = {}
                            for key, value in lug_data.items():
                                expanded[MINIFIED_KEYS.get(key, key)] = value
                            
                            open_lugs.append({
                                'type': expanded.get('type'),
                                'priority': expanded.get('priority'),
                                'title': expanded.get('title')
                            })
                        except Exception:
                            continue
            
            if open_lugs:
                # Store full list for tool use
                point['open_lugs'] = open_lugs
                
                # Group by priority for summary
                high = [l for l in open_lugs if l['priority'] == 'high']
                medium = [l for l in open_lugs if l['priority'] == 'medium']
                low = [l for l in open_lugs if l['priority'] == 'low']
                
                summary_parts = []
                if high:
                    summary_parts.append(f"{len(high)} high")
                if medium:
                    summary_parts.append(f"{len(medium)} medium")
                if low:
                    summary_parts.append(f"{len(low)} low")
                
                point['open_lugs_summary'] = f"{len(open_lugs)} open: " + ", ".join(summary_parts)
                
                # Pick next session lug (highest priority/value)
                # Simple logic: first high priority, or first in list
                significant = sorted(open_lugs, key=lambda x: (x['priority'] == 'high', x.get('value', 0)), reverse=True)
                if significant:
                    point['next_session_lug'] = significant[0]
            else:
                point['open_lugs_summary'] = "No open Lugs"
                point['open_lugs'] = []
        else:
            point['open_lugs_summary'] = "No Lugs system initialized"
        
        return point

    def update_from_state(self):
        """Update point file from current state."""
        self.update_point()
    
    def update_point(self, shipit_summary: Optional[str] = None):
        """
        Update WAI-Point.json with latest state.
        
        Args:
            shipit_summary: Optional shipit summary to include
        """
        point = self.generate_point()
        
        if shipit_summary:
            if not point['last_shipit']:
                point['last_shipit'] = {}
            point['last_shipit']['timestamp'] = datetime.now().isoformat()
            point['last_shipit']['summary'] = shipit_summary
        
        # Write Point
        with open(self.point_file, 'w') as f:
            json.dump(point, f, indent=2)
    
    def load_point(self) -> Optional[Dict[str, Any]]:
        """Load existing WAI-Point.json if exists."""
        if self.point_file.exists():
            with open(self.point_file, 'r') as f:
                return json.load(f)
        return None

    def export_wai_point(self) -> str:
        """
        Export WAI-Point data as a condensed, readable string for AI/Chat.
        
        Returns:
            Formatted string
        """
        point = self.load_point() or self.generate_point()
        
        lines = []
        lines.append(f"📍 WAI-Point: {point['project']['name']} (v{point['project']['version']})")
        lines.append(f"Summary: {point['summary']}")
        lines.append(f"Status: {point['open_lugs_summary']}")
        
        if point.get('last_shipit'):
            ls = point['last_shipit']
            lines.append(f"Last Shipit: {ls.get('summary', 'Unknown')}")
            if ls.get('key_topics'):
                lines.append(f"Topics: {', '.join(ls['key_topics'])}")
        
        if point.get('next_session_lug'):
            next_lug = point['next_session_lug']
            lines.append(f"Next Up: {next_lug['title']} ({next_lug['id'][:8]})")
        
        if point.get('key_learnings'):
            lines.append("\nKey Learnings:")
            for learning in point['key_learnings']:
                lines.append(f"  • {learning}")
        
        return "\n".join(lines)
