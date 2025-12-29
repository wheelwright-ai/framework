"""
Document Analysis Spoke

Enables deep analysis of documents and files.
"""

from ..base import BaseSpoke
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone


class DocumentAnalysisSpoke(BaseSpoke):
    """
    Document Analysis spoke for deep document understanding.

    This spoke helps analyze documents, extract key information,
    and maintain analysis context across sessions.
    """

    @property
    def name(self) -> str:
        return "document-analysis"

    @property
    def description(self) -> str:
        return "Deep analysis of documents, reports, and files."

    def activate(self) -> bool:
        """Activate document analysis for this wheel."""
        self._state = {
            "activated_at": datetime.now(timezone.utc).isoformat(),
            "analyzed_documents": [],
            "key_findings": []
        }
        self.save_state()
        return True

    def deactivate(self) -> bool:
        """Deactivate document analysis for this wheel."""
        spoke_file = self.wheel_path / f"WWAI-Spoke-{self.name}.json"
        if spoke_file.exists():
            spoke_file.unlink()
        return True

    def get_context(self) -> str:
        """Get document analysis context for AI sessions."""
        return """## Document Analysis Spoke

This wheel has document analysis enabled for deep document understanding.

### Capabilities

- **PDF Analysis**: Extract and analyze PDF content
- **Key Point Extraction**: Identify critical information
- **Summary Generation**: Create concise summaries
- **Cross-Reference**: Find connections between documents

### Supported Document Types

- PDF files
- Markdown documents
- Text files
- Code files
- JSON/YAML configurations

### How to Use

1. Share the document or its path
2. Specify the analysis goal:
   - "Extract key requirements from this spec"
   - "Summarize the main points"
   - "Find all action items"
   - "Identify risks and concerns"

### Analysis Output

Analyses are structured as:
- **Summary**: Brief overview
- **Key Points**: Main takeaways (bulleted)
- **Details**: Deeper analysis
- **Actions**: Recommended next steps
- **Questions**: Items needing clarification
"""

    def record_analysis(self, document: str, summary: str, key_points: List[str]) -> None:
        """
        Record a document analysis.

        Args:
            document: Document path or name
            summary: Analysis summary
            key_points: List of key points
        """
        self.load_state()
        self._state.setdefault("analyzed_documents", []).append({
            "date": datetime.now(timezone.utc).isoformat(),
            "document": document,
            "summary": summary,
            "key_points": key_points
        })
        self.save_state()
