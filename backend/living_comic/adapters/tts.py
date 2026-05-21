from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Dict, Optional

from living_comic.models import ComicIssue, ComicPanel


class MacSayTTS:
    def __init__(self, voices: Optional[Dict[str, str]] = None):
        self.voices = voices or {"Calder": "Daniel", "Huemon Trainer": "Eddy (English (US))", "Thor": "Bubbles"}

    def synthesize_dialogue(self, issue: ComicIssue, panel: ComicPanel, out_path: Path) -> Path:
        text = " ".join(f"{d.get('speaker')}: {d.get('text')}" for d in panel.dialogue) or panel.action
        voice = self.voices.get(panel.dialogue[0].get("speaker") if panel.dialogue else "Calder", "Daniel")
        out_path = out_path.with_suffix(".aiff")
        subprocess.run(["say", "-v", voice, "-o", str(out_path), text], check=True)
        return out_path


class VoiceCloneTTS:
    """Voice cloning adapter placeholder for MimikaStudio / Qwen3-TTS / mlx-audio.

    Keep reference clips under project assets/voices/. Implement command or HTTP invocation once the local tool path is known.
    """
    def __init__(self, engine: str = "mlx-audio", reference_clip: Optional[Path] = None):
        self.engine = engine
        self.reference_clip = reference_clip

    def synthesize_dialogue(self, issue: ComicIssue, panel: ComicPanel, out_path: Path) -> Path:
        raise NotImplementedError("Connect local voice cloning command/API after reference clip is provided.")
