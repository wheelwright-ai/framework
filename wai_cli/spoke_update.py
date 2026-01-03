"""
Spoke update and seeding utilities.

Handles seed ingestion, reference archiving, and unknown file cleanup.
"""

from __future__ import annotations

import json
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Any

from .rebalancer import FileRebalancer


class SpokeUpdateProcessor:
    """Process seed folders and keep WAI-Spoke tidy."""

    SEED_README = (
        "# Seed Folders\n\n"
        "Use these folders to bootstrap WAI-Spoke with existing context.\n\n"
        "- seed/ingest: drop background docs to be fully subsumed into WAI files.\n"
        "- seed/reference: drop reference docs to be indexed and archived in reference/.\n\n"
        "After running Update, seed/ingest and seed/reference should be empty.\n"
    )

    def __init__(self, spoke_path: Path):
        self.spoke_path = spoke_path
        self.wai_spoke_dir = spoke_path / "WAI-Spoke"
        self.seed_dir = self.wai_spoke_dir / "seed"
        self.seed_ingest_dir = self.seed_dir / "ingest"
        self.seed_reference_dir = self.seed_dir / "reference"
        self.reference_dir = self.wai_spoke_dir / "reference"
        self.index_file = self.wai_spoke_dir / "WAI-File-Index.json"
        self.state_md = self.wai_spoke_dir / "WAI-State.md"
        self.backlog_md = self.wai_spoke_dir / "WAI-Backlog.md"

    def ensure_seed_structure(self) -> None:
        self.seed_ingest_dir.mkdir(parents=True, exist_ok=True)
        self.seed_reference_dir.mkdir(parents=True, exist_ok=True)
        self.reference_dir.mkdir(parents=True, exist_ok=True)

        readme = self.seed_dir / "README.md"
        if not readme.exists():
            readme.write_text(self.SEED_README)

    def plan_update(self) -> Dict[str, Any]:
        self.ensure_seed_structure()

        ingest_files = self._list_seed_files(self.seed_ingest_dir)
        reference_files = self._list_seed_files(self.seed_reference_dir)

        rebalancer = FileRebalancer(self.wai_spoke_dir)
        unknown_items = rebalancer.scan_unknown_files()

        return {
            "ingest_files": ingest_files,
            "reference_files": reference_files,
            "unknown_items": unknown_items
        }

    def run_update(self) -> Dict[str, Any]:
        self.ensure_seed_structure()

        result = {
            "ingested": [],
            "ingest_notes": [],
            "archived_reference": [],
            "archived_unknown": [],
            "warnings": []
        }

        ingest_files = self._list_seed_files(self.seed_ingest_dir)
        reference_files = self._list_seed_files(self.seed_reference_dir)
        rebalancer = FileRebalancer(self.wai_spoke_dir)
        unknown_items = rebalancer.scan_unknown_files()

        ingested, ingest_notes, ingest_warnings = self._ingest_files(ingest_files)
        result["ingested"] = ingested
        result["ingest_notes"] = ingest_notes
        result["warnings"].extend(ingest_warnings)

        archived_reference = self._archive_reference_files(reference_files, "seeded")
        result["archived_reference"] = archived_reference

        archived_unknown = self._archive_unknown_items(unknown_items)
        result["archived_unknown"] = archived_unknown

        return result

    def review_project(self) -> Dict[str, Any]:
        """Return a quick discovery snapshot of the project."""
        details = {
            "path": str(self.spoke_path),
            "name": self.spoke_path.name,
            "has_wai_spoke": self.wai_spoke_dir.exists(),
            "key_files": [],
            "readme_preview": ""
        }

        candidates = [
            "README.md",
            "README.txt",
            "docs",
            "package.json",
            "pyproject.toml",
            "requirements.txt",
            "Makefile",
            "Dockerfile"
        ]

        for name in candidates:
            path = self.spoke_path / name
            if path.exists():
                details["key_files"].append(str(path.relative_to(self.spoke_path)))

        readme = self.spoke_path / "README.md"
        if readme.exists():
            content = readme.read_text(errors="ignore").splitlines()
            details["readme_preview"] = "\n".join(content[:12])

        return details

    def _list_seed_files(self, folder: Path) -> List[Path]:
        if not folder.exists():
            return []
        items = []
        for item in folder.iterdir():
            if item.name == "README.md":
                continue
            items.append(item)
        return items

    def _ingest_files(self, files: List[Path]) -> (List[str], List[Dict[str, Any]], List[str]):
        if not files:
            return [], [], []

        ingested = []
        notes: List[Dict[str, Any]] = []
        warnings = []
        timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        seed_block = [f"## Seeded Context (Ingested) - {timestamp}", ""]

        backlog_block = []

        for path in files:
            if path.is_dir():
                warnings.append(f"Skipped directory in ingest: {path.name}")
                self._move_to_reference(path, self.reference_dir / "seeded")
                continue

            if not self._is_text_file(path):
                warnings.append(f"Non-text file moved to reference: {path.name}")
                self._move_to_reference(path, self.reference_dir / "seeded")
                continue

            content = path.read_text(errors="ignore").strip()
            if not content:
                path.unlink()
                continue

            preview = content.splitlines()[0] if content.splitlines() else ""
            note = {
                "file": path.name,
                "bytes": path.stat().st_size,
                "preview": preview[:120],
                "applied_to": ["WAI-State.md"]
            }

            seed_block.append(f"### {path.name}")
            seed_block.append("")
            seed_block.append(content)
            seed_block.append("")

            if "todo" in path.name.lower() or "backlog" in path.name.lower():
                backlog_block.append(f"### {path.name}")
                backlog_block.append("")
                backlog_block.append(content)
                backlog_block.append("")
                note["applied_to"].append("WAI-Backlog.md")

            path.unlink()
            ingested.append(path.name)
            notes.append(note)

        if seed_block and self.state_md.exists():
            existing = self.state_md.read_text()
            self.state_md.write_text(existing.rstrip() + "\n\n" + "\n".join(seed_block).rstrip() + "\n")

        if backlog_block and self.backlog_md.exists():
            existing = self.backlog_md.read_text()
            self.backlog_md.write_text(existing.rstrip() + "\n\n## Seeded Backlog\n\n" + "\n".join(backlog_block).rstrip() + "\n")

        if ingested:
            self._record_seed_ingest(ingested, notes)

        return ingested, notes, warnings

    def _archive_reference_files(self, files: List[Path], bucket: str) -> List[str]:
        if not files:
            return []

        archived = []
        dest_root = self.reference_dir / bucket
        dest_root.mkdir(parents=True, exist_ok=True)

        for path in files:
            dest = self._move_to_reference(path, dest_root)
            archived.append(str(dest.relative_to(self.wai_spoke_dir)))
            self._record_reference_entry(dest, "Seeded reference material")

        return archived

    def _archive_unknown_items(self, items: List[Path]) -> List[str]:
        if not items:
            return []

        archived = []
        dest_root = self.reference_dir / "auto"
        dest_root.mkdir(parents=True, exist_ok=True)

        for path in items:
            dest = self._move_to_reference(path, dest_root)
            archived.append(str(dest.relative_to(self.wai_spoke_dir)))
            self._record_reference_entry(dest, "Auto-archived from WAI-Spoke root")

        return archived

    def _move_to_reference(self, path: Path, dest_root: Path) -> Path:
        dest_root.mkdir(parents=True, exist_ok=True)
        dest = dest_root / path.name
        if dest.exists():
            suffix = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
            dest = dest_root / f"{path.stem}-{suffix}{path.suffix}"
        shutil.move(str(path), str(dest))
        return dest

    def _record_seed_ingest(self, ingested_files: List[str], notes: List[Dict[str, Any]]) -> None:
        index = self._load_index()
        meta = index.setdefault("metadata", {})
        seed_log = meta.setdefault("seed_ingest", [])
        seed_log.append({
            "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "files": ingested_files,
            "notes": notes
        })
        self._save_index(index)

    def _record_reference_entry(self, dest: Path, purpose: str) -> None:
        index = self._load_index()
        project_files = index.setdefault("project_files", {})
        rel_path = str(dest.relative_to(self.wai_spoke_dir))
        project_files.setdefault(rel_path, {
            "purpose": purpose,
            "required": False,
            "auto_managed": True
        })
        self._save_index(index)

    def _load_index(self) -> Dict[str, Any]:
        if self.index_file.exists():
            try:
                return json.loads(self.index_file.read_text())
            except Exception:
                pass
        return {
            "version": "1.0",
            "metadata": {
                "spoke_path": str(self.wai_spoke_dir),
                "project_root": str(self.spoke_path),
                "project_name": self.spoke_path.name,
                "last_updated": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
                "updated_by": "WAI Update"
            },
            "core_files": {},
            "operational_files": {},
            "project_files": {},
            "legacy_files": {}
        }

    def _save_index(self, index: Dict[str, Any]) -> None:
        meta = index.setdefault("metadata", {})
        meta["last_updated"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        meta["updated_by"] = "WAI Update"
        self.index_file.write_text(json.dumps(index, indent=2))

    def _is_text_file(self, path: Path) -> bool:
        try:
            with open(path, "rb") as f:
                chunk = f.read(2048)
            return b"\x00" not in chunk
        except Exception:
            return False
