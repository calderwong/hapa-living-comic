from __future__ import annotations

import urllib.request
from pathlib import Path
from typing import Optional

from living_comic.models import ComicIssue, ComicPanel


class ComfyUIImageGenerator:
    """Comfy/custom image node adapter placeholder.

    Configure workflow_json with API-format ComfyUI graph, then map prompt/image outputs in a project-specific pass.
    The mock generator is used by default until your custom node workflow is provided.
    """
    def __init__(self, host: str = "http://127.0.0.1:8188", workflow_json: Optional[Path] = None):
        self.host = host.rstrip("/")
        self.workflow_json = Path(workflow_json) if workflow_json else None

    def health(self) -> bool:
        try:
            with urllib.request.urlopen(f"{self.host}/system_stats", timeout=2) as r:
                return r.status == 200
        except Exception:
            return False

    def generate_panel(self, issue: ComicIssue, panel: ComicPanel, out_path: Path) -> Path:
        raise NotImplementedError("Provide the custom image generation workflow mapping for this node.")
