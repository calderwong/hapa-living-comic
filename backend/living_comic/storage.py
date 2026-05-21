from __future__ import annotations

import json
from pathlib import Path
from typing import List

from .models import ComicIssue, utc_now


class ProjectStore:
    """Filesystem project store: project JSON plus asset folder."""

    def __init__(self, root: Path):
        self.root = Path(root)
        self.projects_dir = self.root / "projects"
        self.assets_dir = self.root / "assets"
        self.projects_dir.mkdir(parents=True, exist_ok=True)
        self.assets_dir.mkdir(parents=True, exist_ok=True)

    def save_issue(self, issue: ComicIssue) -> Path:
        issue.updated_at = utc_now()
        path = self.projects_dir / f"{issue.id}.json"
        path.write_text(json.dumps(issue.to_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
        return path

    def load_issue(self, file_name_or_id: str) -> ComicIssue:
        name = file_name_or_id if file_name_or_id.endswith(".json") else f"{file_name_or_id}.json"
        path = self.projects_dir / name
        return ComicIssue.from_dict(json.loads(path.read_text(encoding="utf-8")))

    def list_issues(self) -> List[ComicIssue]:
        return [self.load_issue(p.name) for p in sorted(self.projects_dir.glob("*.json"))]

    def asset_path(self, relative: str) -> Path:
        path = self.assets_dir / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        return path
