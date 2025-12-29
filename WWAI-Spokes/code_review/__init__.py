"""
Code Review Spoke

Enables comprehensive code review and suggestions.
"""

from ..base import BaseSpoke
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone


class CodeReviewSpoke(BaseSpoke):
    """
    Code Review spoke for comprehensive code analysis.

    This spoke provides structured code review with focus on
    security, performance, clarity, and best practices.
    """

    @property
    def name(self) -> str:
        return "code-review"

    @property
    def description(self) -> str:
        return "Comprehensive code review and suggestions."

    def activate(self) -> bool:
        """Activate code review for this wheel."""
        self._state = {
            "activated_at": datetime.now(timezone.utc).isoformat(),
            "reviews": [],
            "focus_areas": ["security", "performance", "clarity", "best-practices"]
        }
        self.save_state()
        return True

    def deactivate(self) -> bool:
        """Deactivate code review for this wheel."""
        spoke_file = self.wheel_path / f"WWAI-Spoke-{self.name}.json"
        if spoke_file.exists():
            spoke_file.unlink()
        return True

    def get_context(self) -> str:
        """Get code review context for AI sessions."""
        return """## Code Review Spoke

This wheel has code review enabled for comprehensive code analysis.

### Review Focus Areas

1. **Security**
   - Input validation
   - Authentication/authorization
   - Injection vulnerabilities
   - Sensitive data handling

2. **Performance**
   - Algorithm efficiency
   - Resource usage
   - Caching opportunities
   - Query optimization

3. **Clarity**
   - Naming conventions
   - Code organization
   - Comments and documentation
   - Function/method size

4. **Best Practices**
   - Design patterns
   - Error handling
   - Testing coverage
   - Code duplication

### How to Request Review

- "Review this function for security issues"
- "Check this PR for performance problems"
- "Full code review of this module"
- "Quick review focusing on clarity"

### Review Output Format

```markdown
## Code Review: [file/component]

### Summary
[Brief overall assessment]

### Issues Found

#### Critical
- [Issue 1]

#### Important
- [Issue 2]

#### Suggestions
- [Improvement idea]

### Positive Notes
- [What's done well]

### Recommended Actions
1. [Action 1]
2. [Action 2]
```
"""

    def record_review(self, target: str, findings: Dict[str, List[str]]) -> None:
        """
        Record a code review.

        Args:
            target: What was reviewed (file, PR, etc.)
            findings: Dict of finding categories to lists of findings
        """
        self.load_state()
        self._state.setdefault("reviews", []).append({
            "date": datetime.now(timezone.utc).isoformat(),
            "target": target,
            "findings": findings
        })
        self.save_state()
