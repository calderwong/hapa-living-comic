from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
import uuid


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def new_id(prefix: str) -> str:
    return f"{prefix}-{uuid.uuid4().hex[:12]}"


@dataclass
class ComicPanel:
    id: str
    page: int
    panel: int
    action: str
    dialogue: List[Dict[str, str]] = field(default_factory=list)
    visual_prompt: str = ""
    camera: str = ""
    composition: str = ""
    lighting: str = ""
    emotion: str = ""
    image_path: Optional[str] = None
    video_path: Optional[str] = None
    audio_path: Optional[str] = None
    duration_seconds: float = 5.0
    status: str = "scripted"

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ComicPanel":
        return cls(**data)


@dataclass
class ComicIssue:
    id: str
    title: str
    logline: str
    style: str
    panels: List[ComicPanel] = field(default_factory=list)
    created_at: str = field(default_factory=utc_now)
    updated_at: str = field(default_factory=utc_now)
    source_idea: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["panels"] = [p.to_dict() for p in self.panels]
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ComicIssue":
        payload = dict(data)
        payload["panels"] = [ComicPanel.from_dict(p) for p in payload.get("panels", [])]
        return cls(**payload)
