"""
Template Wheels System for Wheelwright Framework.

Enables creating reusable project templates from well-structured spokes
and using them to initialize new projects faster with best practices baked in.
"""

import json
import shutil
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime


class TemplateManager:
    """Manages project templates for faster spoke initialization."""

    def __init__(self, hub_path: Optional[Path] = None):
        """
        Initialize template manager.

        Args:
            hub_path: Path to hub directory (default: auto-discover)
        """
        self.hub_path = hub_path
        if hub_path:
            self.templates_dir = hub_path / 'templates'
            self.templates_dir.mkdir(exist_ok=True)

    def create_template(
        self,
        spoke_path: Path,
        template_name: str,
        description: str = "",
        questions: Optional[List[Dict[str, str]]] = None
    ) -> Dict[str, Any]:
        """
        Create a template from an existing spoke.

        Args:
            spoke_path: Path to source spoke
            template_name: Name for the template
            description: Template description
            questions: Optional list of questions to ask when using template

        Returns:
            Dict with template creation results
        """
        if not self.hub_path:
            raise ValueError("Hub path required for template creation")

        wai_spoke = spoke_path / 'WAI-Spoke'
        if not wai_spoke.exists():
            raise ValueError(f"No WAI-Spoke found at {spoke_path}")

        # Create template directory
        template_dir = self.templates_dir / template_name
        if template_dir.exists():
            raise ValueError(f"Template '{template_name}' already exists")

        template_dir.mkdir(parents=True)

        # Analyze spoke structure
        analysis = self._analyze_spoke(wai_spoke)

        # Copy WAI files as template base
        template_wai = template_dir / 'WAI-Spoke'
        template_wai.mkdir()

        # Copy essential files (excluding session-specific data)
        essential_files = ['WAI-Guide.md', 'WAI-State.md']
        for file_name in essential_files:
            src = wai_spoke / file_name
            if src.exists():
                shutil.copy2(src, template_wai / file_name)

        # Create template metadata
        metadata = {
            'name': template_name,
            'description': description,
            'created_at': datetime.now().isoformat(),
            'created_from': str(spoke_path),
            'questions': questions or [],
            'structure': analysis,
            'version': '1.0'
        }

        metadata_file = template_dir / 'template.json'
        with open(metadata_file, 'w') as f:
            json.dump(metadata, f, indent=2)

        # Create README
        readme = self._generate_template_readme(metadata)
        with open(template_dir / 'README.md', 'w') as f:
            f.write(readme)

        return {
            'success': True,
            'template_name': template_name,
            'template_path': str(template_dir),
            'files_included': len(essential_files),
            'analysis': analysis
        }

    def list_templates(self) -> List[Dict[str, Any]]:
        """
        List available templates.

        Returns:
            List of template metadata dicts
        """
        if not self.hub_path or not self.templates_dir.exists():
            return []

        templates = []
        for template_dir in self.templates_dir.iterdir():
            if not template_dir.is_dir():
                continue

            metadata_file = template_dir / 'template.json'
            if metadata_file.exists():
                with open(metadata_file) as f:
                    metadata = json.load(f)
                    templates.append(metadata)

        return sorted(templates, key=lambda t: t['created_at'], reverse=True)

    def apply_template(
        self,
        template_name: str,
        target_path: Path,
        answers: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Apply a template to create a new spoke.

        Args:
            template_name: Name of template to apply
            target_path: Where to create the new spoke
            answers: Answers to template questions

        Returns:
            Dict with application results
        """
        if not self.hub_path:
            raise ValueError("Hub path required for template application")

        template_dir = self.templates_dir / template_name
        if not template_dir.exists():
            raise ValueError(f"Template '{template_name}' not found")

        # Load template metadata
        metadata_file = template_dir / 'template.json'
        with open(metadata_file) as f:
            metadata = json.load(f)

        # Check if target already has WAI-Spoke
        target_wai = target_path / 'WAI-Spoke'
        if target_wai.exists():
            raise ValueError(f"WAI-Spoke already exists at {target_path}")

        # Copy template WAI files
        template_wai = template_dir / 'WAI-Spoke'
        shutil.copytree(template_wai, target_wai)

        # Apply customizations from answers
        if answers:
            self._apply_customizations(target_wai, answers)

        # Initialize fresh state
        self._initialize_state(target_wai, metadata, answers)

        return {
            'success': True,
            'template_used': template_name,
            'spoke_path': str(target_wai),
            'customizations_applied': len(answers) if answers else 0
        }

    def delete_template(self, template_name: str) -> bool:
        """
        Delete a template.

        Args:
            template_name: Name of template to delete

        Returns:
            True if deleted successfully
        """
        if not self.hub_path:
            raise ValueError("Hub path required")

        template_dir = self.templates_dir / template_name
        if not template_dir.exists():
            return False

        shutil.rmtree(template_dir)
        return True

    def _analyze_spoke(self, wai_spoke: Path) -> Dict[str, Any]:
        """Analyze spoke structure for template metadata."""
        analysis = {
            'files_present': [],
            'project_type': 'general',
            'has_tests': False,
            'has_docs': False
        }

        # Check WAI files
        for wai_file in wai_spoke.iterdir():
            if wai_file.is_file():
                analysis['files_present'].append(wai_file.name)

        # Check parent directory for project clues
        parent = wai_spoke.parent

        # Detect project type
        if (parent / 'package.json').exists():
            analysis['project_type'] = 'nodejs'
        elif (parent / 'requirements.txt').exists() or (parent / 'setup.py').exists():
            analysis['project_type'] = 'python'
        elif (parent / 'Cargo.toml').exists():
            analysis['project_type'] = 'rust'
        elif (parent / 'go.mod').exists():
            analysis['project_type'] = 'go'

        # Check for tests
        test_patterns = ['test', 'tests', 'spec', '__tests__']
        for pattern in test_patterns:
            if list(parent.glob(f'**/{pattern}')):
                analysis['has_tests'] = True
                break

        # Check for docs
        if (parent / 'docs').exists() or (parent / 'README.md').exists():
            analysis['has_docs'] = True

        return analysis

    def _generate_template_readme(self, metadata: Dict[str, Any]) -> str:
        """Generate README for template."""
        return f"""# {metadata['name']} Template

{metadata['description']}

## Created
- Date: {metadata['created_at']}
- From: {metadata['created_from']}

## Project Type
{metadata['structure']['project_type']}

## Includes
- WAI-Guide.md - AI instructions
- WAI-State.md - Strategic context template

## Questions Asked
{self._format_questions(metadata['questions'])}

## Usage

```bash
WAI-CLI template apply "{metadata['name']}" /path/to/new/project
```

---

*Generated by Wheelwright Template System*
"""

    def _format_questions(self, questions: List[Dict[str, str]]) -> str:
        """Format questions for README."""
        if not questions:
            return "None - uses defaults"

        lines = []
        for q in questions:
            lines.append(f"- {q.get('question', 'N/A')}")
        return '\n'.join(lines)

    def _apply_customizations(self, target_wai: Path, answers: Dict[str, str]) -> None:
        """Apply customizations based on answers."""
        # For now, just store answers in state
        # Future: template variables replacement
        pass

    def _initialize_state(
        self,
        target_wai: Path,
        metadata: Dict[str, Any],
        answers: Optional[Dict[str, str]]
    ) -> None:
        """Initialize fresh state for new spoke from template."""
        # Create fresh WAI-State.json
        state_template = {
            "_wheel_metadata": {
                "name": "New Project",
                "created_from_template": metadata['name'],
                "template_version": metadata['version'],
                "created_at": datetime.now().isoformat()
            },
            "_project_foundation": {
                "completed": False,
                "problem_statement": "",
                "objectives": [],
                "boundaries": {
                    "in_scope": [],
                    "out_of_scope": [],
                    "deferred": []
                }
            },
            "decisions": [],
            "features": [],
            "bugs": [],
            "context": {
                "current_phase": "Foundation Setup",
                "next_actions": [
                    "Complete project foundation questionnaire",
                    "Review and customize WAI-Guide.md",
                    "Start first development session"
                ],
                "recent_changes": []
            },
            "_session_state": {
                "current_session": None,
                "last_closeout": None,
                "protocol_completed": False,
                "requires_review": False
            },
            "analytics": {
                "sessions": {
                    "total_count": 0,
                    "total_turns": 0,
                    "total_duration_seconds": 0,
                    "avg_duration_seconds": 0
                },
                "token_efficiency": {
                    "total_tokens_used": 0,
                    "context_limit": 200000,
                    "avg_tokens_per_session": 0
                },
                "time_tracking": {
                    "total_time_together_seconds": 0,
                    "total_time_ai_alone_seconds": 0
                },
                "baseline_mode": {
                    "enabled": False,
                    "total_tokens_used": 0,
                    "total_sessions": 0,
                    "description": "Track metrics without Wheelwright optimizations for comparison"
                },
                "ai_wins": [],
                "last_updated": None
            }
        }

        # Apply answers if provided
        if answers:
            if 'project_name' in answers:
                state_template['_wheel_metadata']['name'] = answers['project_name']
            if 'problem_statement' in answers:
                state_template['_project_foundation']['problem_statement'] = answers['problem_statement']

        state_file = target_wai / 'WAI-State.json'
        with open(state_file, 'w') as f:
            json.dump(state_template, f, indent=2)

        # Create other essential files
        (target_wai / 'WAI-Signals.jsonl').touch()
        (target_wai / 'WAI-KB-Sync.json').write_text('{"last_sync": null, "version": 1}')
