from __future__ import annotations

import json
import os
import shlex
import subprocess
from pathlib import Path
from typing import Dict, Optional

from living_comic.models import ComicIssue, ComicPanel


def panel_dialogue_text(panel: ComicPanel) -> str:
    return " ".join(f"{d.get('speaker')}: {d.get('text')}" for d in panel.dialogue) or panel.action


class MacSayTTS:
    def __init__(self, voices: Optional[Dict[str, str]] = None):
        self.voices = voices or {
            "Calder": os.environ.get("LIVING_COMIC_VOICE_CALDER", "Daniel"),
            "Huemon Trainer": os.environ.get("LIVING_COMIC_VOICE_TRAINER", "Eddy (English (US))"),
            "Thor": os.environ.get("LIVING_COMIC_VOICE_THOR", "Bubbles"),
        }

    def synthesize_dialogue(self, issue: ComicIssue, panel: ComicPanel, out_path: Path) -> Path:
        text = panel_dialogue_text(panel)
        speaker = str(panel.dialogue[0].get("speaker") if panel.dialogue else "Calder")
        voice = self.voices.get(speaker, "Daniel")
        out_path = out_path.with_suffix(".aiff")
        out_path.parent.mkdir(parents=True, exist_ok=True)
        subprocess.run(["say", "-v", voice, "-o", str(out_path), text], check=True)
        return out_path


class LocalCommandVoiceCloneTTS:
    """Command-template adapter for local voice cloning tools.

    Configure with LIVING_COMIC_TTS_CMD, for example:
      mlx-audio tts --text {text_json} --voice {speaker_json} --ref {reference_clip} --output {out}

    Placeholders:
      {text}, {text_json}, {speaker}, {speaker_json}, {out}, {reference_clip}, {panel_id}, {issue_id}
    """

    def __init__(self, command_template: Optional[str] = None, reference_clip: Optional[Path] = None):
        self.command_template = command_template or os.environ.get("LIVING_COMIC_TTS_CMD")
        self.reference_clip = Path(reference_clip or os.environ.get("LIVING_COMIC_VOICE_REFERENCE", "")).expanduser() if (reference_clip or os.environ.get("LIVING_COMIC_VOICE_REFERENCE")) else None
        if not self.command_template:
            raise RuntimeError("LIVING_COMIC_TTS_CMD is required for command/voice-clone TTS provider")
        self.command_template = str(self.command_template)

    def synthesize_dialogue(self, issue: ComicIssue, panel: ComicPanel, out_path: Path) -> Path:
        text = panel_dialogue_text(panel)
        speaker = str(panel.dialogue[0].get("speaker") if panel.dialogue else "Calder")
        out_path = out_path.with_suffix(os.environ.get("LIVING_COMIC_TTS_EXT", ".wav"))
        out_path.parent.mkdir(parents=True, exist_ok=True)
        values = {
            "text": shlex.quote(text),
            "text_json": shlex.quote(json.dumps(text)),
            "speaker": shlex.quote(str(speaker)),
            "speaker_json": shlex.quote(json.dumps(str(speaker))),
            "out": shlex.quote(str(out_path)),
            "reference_clip": shlex.quote(str(self.reference_clip or "")),
            "panel_id": shlex.quote(panel.id),
            "issue_id": shlex.quote(issue.id),
        }
        command = self.command_template.format(**values)
        subprocess.run(command, shell=True, check=True)
        if not out_path.exists():
            raise RuntimeError(f"TTS command completed but did not create {out_path}")
        return out_path


VoiceCloneTTS = LocalCommandVoiceCloneTTS
