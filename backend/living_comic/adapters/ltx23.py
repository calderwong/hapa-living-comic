from __future__ import annotations

from pathlib import Path
from typing import Optional

from living_comic.models import ComicIssue, ComicPanel


class LTX23Animator:
    """LTX 2.3 image-to-video adapter interface.

    Expected integration: submit panel image + prompt/camera notes to your LTX 2.3 local node, poll job, download mp4.
    """
    def __init__(self, endpoint: str = "http://127.0.0.1:8188", workflow_json: Optional[Path] = None):
        self.endpoint = endpoint.rstrip("/")
        self.workflow_json = Path(workflow_json) if workflow_json else None

    def animate_panel(self, issue: ComicIssue, panel: ComicPanel, image_path: Path, out_path: Path) -> Path:
        raise NotImplementedError("Connect LTX 2.3 image-to-video workflow here.")
