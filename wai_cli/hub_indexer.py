"""
Hub Indexer Module (Map & Compass)

Generates a content index (Map) for the Hub to help Spokes navigate available knowledge.
"""

import os
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime
import json

class HubIndexer:
    """Generates WAI-Hub-Index.md from hub content."""
    
    def __init__(self, hub_path: Path):
        self.hub_path = hub_path
        self.index_path = hub_path / "WAI-Hub-Index.md"
        
    def generate_index(self) -> Path:
        """
        Scan hub and generate the index file.
        
        Returns:
            Path to the generated index file.
        """
        print(f"  🗺️  Generating Hub Index (The Map)...")
        
        # 1. Gather stats
        stats = self._gather_stats()
        
        # 2. Scan knowledge files
        knowledge_files = self._scan_knowledge_files()
        
        # 3. Create index content
        content = self._build_index_content(stats, knowledge_files)
        
        # 4. Write to file
        with open(self.index_path, 'w', encoding='utf-8') as f:
            f.write(content)
            
        return self.index_path
        
    def _gather_stats(self) -> Dict[str, Any]:
        """Gather accumulated statistics from the hub."""
        # TODO: Read from a hypothetical stats file or count files
        # For now, simplistic stats
        return {
            "projects_connected": self._count_projects(),
            "total_files": self._count_files(),
            "last_updated": datetime.now().isoformat()
        }
        
    def _count_projects(self) -> int:
        registry = self.hub_path / 'registry' / 'wheel-projects.json'
        if registry.exists():
            try:
                data = json.loads(registry.read_text())
                return len(data.get('projects', []))
            except:
                return 0
        return 0
        
    def _count_files(self) -> int:
        count = 0
        for _ in self.hub_path.glob("**/*"):
            count += 1
        return count

    def _scan_knowledge_files(self) -> List[Dict[str, str]]:
        """Scan for markdown files that represent knowledge."""
        knowledge = []
        
        # Simple scan of specific directories or root
        # prioritizing 'patterns', 'decisions', 'learnings' folders if they exist
        # or just root .md files for now (excluding system files)
        
        skip_files = {'WAI-Hub-Index.md', 'README.md', 'hub-profile.json'}
        
        for item in self.hub_path.rglob("*.md"):
            if item.name in skip_files:
                continue
                
            # Start relative path from hub root
            rel_path = item.relative_to(self.hub_path)
            
            # Extract title/description if possible (read first few lines)
            summary = self._extract_summary(item)
            
            knowledge.append({
                "path": str(rel_path),
                "name": item.stem.replace('-', ' ').title(),
                "summary": summary,
                "category": rel_path.parent.name if rel_path.parent != self.hub_path else "General"
            })
            
        return sorted(knowledge, key=lambda x: x['category'])

    def _extract_summary(self, path: Path) -> str:
        """Extract a brief summary from file content."""
        try:
            with open(path, 'r', encoding='utf-8') as f:
                # Read first 5 lines
                lines = [next(f).strip() for _ in range(5)]
                
            # Look for description or just take first non-header line
            for line in lines:
                if line and not line.startswith('#'):
                    return line[:100] + "..." if len(line) > 100 else line
            return "No description available."
        except:
            return "Could not read file."

    def _build_index_content(self, stats: Dict[str, Any], knowledge: List[Dict[str, str]]) -> str:
        """Build the Markdown content for the index."""
        
        # Header
        content = f"# 🗺️ Wheelwright Hub Index (The Map)\n\n"
        content += f"**Hub Status:**\n"
        content += f"- Last Updated: {stats['last_updated']}\n"
        content += f"- Projects Connected: {stats['projects_connected']}\n"
        content += f"- Total Resources: {stats['total_files']}\n\n"
        
        content += "---\n\n"
        content += "## 📚 Available Knowledge\n\n"
        
        if not knowledge:
            content += "*No shared knowledge files found yet.*\n"
        else:
            current_category = ""
            for item in knowledge:
                if item['category'] != current_category:
                    content += f"### 📂 {item['category'].title()}\n\n"
                    current_category = item['category']
                
                content += f"- **[{item['name']}]({item['path']})**\n"
                content += f"  - {item['summary']}\n"
        
        content += "\n---\n\n"
        content += "## 🧭 How to Use\n\n"
        content += "1. **Consult this Map** to find relevant patterns or solutions.\n"
        content += "2. **Read specific files** using `WAI read <path>` (future).\n"
        content += "3. **Apply patterns** to your project.\n"
        
        return content
