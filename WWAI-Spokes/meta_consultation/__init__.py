"""
Meta-Consultation Spoke

Enables querying multiple AI models for diverse perspectives.
"""

from ..base import BaseSpoke
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone


class MetaConsultationSpoke(BaseSpoke):
    """
    Meta-Consultation spoke for multi-AI queries.

    This spoke helps users get diverse perspectives by framing
    questions for multiple AI models and synthesizing responses.
    """

    @property
    def name(self) -> str:
        return "meta-consultation"

    @property
    def description(self) -> str:
        return "Get diverse perspectives by consulting multiple AI models."

    def activate(self) -> bool:
        """Activate meta-consultation for this wheel."""
        self._state = {
            "activated_at": datetime.now(timezone.utc).isoformat(),
            "consultations": [],
            "preferred_models": ["Claude", "GPT-4", "Gemini"]
        }
        self.save_state()
        return True

    def deactivate(self) -> bool:
        """Deactivate meta-consultation for this wheel."""
        spoke_file = self.wheel_path / f"WWAI-Spoke-{self.name}.json"
        if spoke_file.exists():
            spoke_file.unlink()
        return True

    def get_context(self) -> str:
        """Get meta-consultation context for AI sessions."""
        return """## Meta-Consultation Spoke

This wheel has meta-consultation enabled for getting diverse AI perspectives.

### When to Use

- Complex architectural decisions
- Validating important choices
- Getting alternative approaches
- Breaking through analysis paralysis

### How to Invoke

Ask for a meta-consultation:
- "Let's do a meta-consultation on this architecture choice"
- "Can you frame this question for multiple AI perspectives?"
- "I need diverse viewpoints on this decision"

### Process

1. **Frame**: Clearly state the question/decision
2. **Query**: The user will query 2-3 different AI models
3. **Synthesize**: Combine insights from all responses
4. **Document**: Record the consensus and rationale

### Best Practices

- Frame questions neutrally to avoid bias
- Include relevant context for each model
- Note which model provided which insight
- Document disagreements, not just consensus
"""

    def record_consultation(self, topic: str, models: List[str], synthesis: str) -> None:
        """
        Record a completed consultation.

        Args:
            topic: The topic consulted on
            models: List of models queried
            synthesis: The synthesized conclusion
        """
        self.load_state()
        self._state.setdefault("consultations", []).append({
            "date": datetime.now(timezone.utc).isoformat(),
            "topic": topic,
            "models": models,
            "synthesis": synthesis
        })
        self.save_state()
