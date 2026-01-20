"""
Interactive Wizard for Project Initialization.
Queries the user and the Hub to create a smarter project foundation.
"""

from typing import Dict, List, Optional
from pathlib import Path
from ..utils.input import safe_input, safe_confirm, print_info, print_success, print_warning
from ..hub import HubManager

class InitWizard:
    def __init__(self, hub_path: Optional[Path] = None):
        self.hub = HubManager()
        self.hub_path = hub_path
        self.answers: Dict[str, str] = {}
        self.insights: List[str] = []

    def run_interview(self) -> Dict[str, str]:
        """Run the project setup interview."""
        print_info("\n=== Project Vision Interview ===\n")
        
        # 1. Project Type
        print_info("What type of project is this?")
        print_info("Common tags: web, python, cli, react, library, research")
        tags_input = safe_input("Project Tags (comma separated)", default="general")
        self.answers["tags"] = [t.strip().lower() for t in tags_input.split(",")]

        # 2. Description
        description = safe_input("Short Description (one liner)", 
                               default="A new project initialized with Wheelwright")
        self.answers["description"] = description
        
        # 3. Consult Hub
        self._consult_hub()
        
        return self.answers

    def _consult_hub(self):
        """Query Hub for insights based on tags."""
        tags = self.answers.get("tags", [])
        print_info(f"\nScanning Hub for insights on: {', '.join(tags)}...")
        
        found_insights = self.hub.get_insights(tags, hub_path=self.hub_path)
        
        if found_insights:
            print_success(f"\nI found {len(found_insights)} relevant insights from your other projects:")
            for i, insight in enumerate(found_insights, 1):
                print_info(f"  {i}. {insight}")
                self.insights.append(insight)
                
            use_insights = safe_confirm("\nInject these insights into your new WAI-State.md?", default=True)
            self.answers["use_insights"] = use_insights
        else:
            print_info("No specific insights found yet. We'll start fresh.")
            self.answers["use_insights"] = False

    def generate_seed_content(self) -> str:
        """Generate markdown content to seed WAI-State.md."""
        content = [
            f"## Strategic Vision",
            f"",
            f"{self.answers.get('description')}",
            f"",
            f"### Project Tags",
            f"- {', '.join(self.answers.get('tags', []))}",
        ]
        
        if self.answers.get("use_insights") and self.insights:
            content.append("")
            content.append("### Hub Insights (Applied)")
            for insight in self.insights:
                content.append(f"- {insight}")
                
        return "\n".join(content)
