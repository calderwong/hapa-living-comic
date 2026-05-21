from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import List, Protocol

from .models import ComicIssue, ComicPanel, new_id
from .storage import ProjectStore


class LLMAdapter(Protocol):
    def write_issue(self, idea: str, panel_count: int, style: str) -> ComicIssue: ...

class ImageGenerator(Protocol):
    def generate_panel(self, issue: ComicIssue, panel: ComicPanel, out_path: Path) -> Path: ...

class Animator(Protocol):
    def animate_panel(self, issue: ComicIssue, panel: ComicPanel, image_path: Path, out_path: Path) -> Path: ...

class TTSAdapter(Protocol):
    def synthesize_dialogue(self, issue: ComicIssue, panel: ComicPanel, out_path: Path) -> Path: ...


class MockLLM:
    def write_issue(self, idea: str, panel_count: int = 6, style: str = "dark ink cinematic comic") -> ComicIssue:
        panels: List[ComicPanel] = []
        for idx in range(panel_count):
            panels.append(ComicPanel(
                id=f"panel-{idx+1}",
                page=1 + idx // 6,
                panel=1 + idx % 6,
                action=f"Beat {idx+1}: {idea} unfolds as a living comic moment.",
                dialogue=[{"speaker": "Calder" if idx % 3 == 0 else "Huemon Trainer" if idx % 3 == 1 else "Thor", "text": "We keep the campfire honest." if idx % 3 != 2 else "Mrrp."}],
                visual_prompt=f"{style}; panel {idx+1}; {idea}; expressive composition; speech bubble safe area",
                camera="smooth slow push-in with parallax layers",
                composition="classic comic panel, strong gutters, cinematic focal point",
                lighting="moody rim light, luminous UI glow",
                emotion="curious, mythic, playful",
            ))
        return ComicIssue(
            id=new_id("issue"),
            title=idea.title()[:80],
            logline=f"A living comic generated from: {idea}",
            style=style,
            panels=panels,
            source_idea=idea,
        )


class HermesLLM:
    """Hermes subprocess adapter. Uses JSON contract; falls back to MockLLM if parsing fails."""
    def __init__(self, profile: str = "default", timeout: int = 240):
        self.profile = profile
        self.timeout = timeout

    def write_issue(self, idea: str, panel_count: int = 8, style: str = "dark polished comic") -> ComicIssue:
        prompt = (
            "Write a comic issue as strict JSON with fields title, logline, panels. "
            "Each panel must include action, dialogue array of speaker/text, visual_prompt, camera, composition, lighting, emotion. "
            f"Panel count: {panel_count}. Style: {style}. Idea: {idea}"
        )
        try:
            proc = subprocess.run(["hermes", "chat", "-p", self.profile, "-q", prompt], text=True, capture_output=True, timeout=self.timeout)
            raw = proc.stdout.strip()
            start, end = raw.find("{"), raw.rfind("}")
            data = json.loads(raw[start:end+1])
            panels = []
            for i, p in enumerate(data.get("panels", []), 1):
                panels.append(ComicPanel(
                    id=f"panel-{i}", page=1 + (i-1)//6, panel=1 + (i-1)%6,
                    action=p.get("action", ""), dialogue=p.get("dialogue", []),
                    visual_prompt=p.get("visual_prompt", ""), camera=p.get("camera", ""),
                    composition=p.get("composition", ""), lighting=p.get("lighting", ""), emotion=p.get("emotion", ""),
                ))
            return ComicIssue(id=new_id("issue"), title=data.get("title", idea[:80]), logline=data.get("logline", idea), style=style, panels=panels, source_idea=idea)
        except Exception:
            return MockLLM().write_issue(idea, panel_count, style)


class MockImageGenerator:
    def generate_panel(self, issue: ComicIssue, panel: ComicPanel, out_path: Path) -> Path:
        title = issue.title.replace('&', '&amp;').replace('<', '&lt;')
        action = panel.action.replace('&', '&amp;').replace('<', '&lt;')
        prompt = panel.visual_prompt.replace('&', '&amp;').replace('<', '&lt;')
        svg = f'<svg xmlns="http://www.w3.org/2000/svg" width="1280" height="800"><rect width="100%" height="100%" fill="#11131d"/><rect x="40" y="40" width="1200" height="720" rx="28" fill="#1d2438" stroke="#f2d16b" stroke-width="8"/><text x="80" y="120" fill="#f8f3df" font-size="42" font-family="Helvetica">{title}</text><text x="80" y="200" fill="#9fdcff" font-size="30" font-family="Helvetica">Panel {panel.panel}</text><foreignObject x="80" y="250" width="1120" height="420"><div xmlns="http://www.w3.org/1999/xhtml" style="color:white;font:34px Helvetica;line-height:1.25">{action}<br/><br/>{prompt}</div></foreignObject></svg>'
        out_path.write_text(svg, encoding="utf-8")
        return out_path


class MockLTXAnimator:
    def animate_panel(self, issue: ComicIssue, panel: ComicPanel, image_path: Path, out_path: Path) -> Path:
        out_path.write_text(f"Mock LTX 2.3 image-to-video placeholder for {panel.id} based on {image_path.name}\n", encoding="utf-8")
        return out_path


class MockTTS:
    def synthesize_dialogue(self, issue: ComicIssue, panel: ComicPanel, out_path: Path) -> Path:
        text = " ".join(f"{d.get('speaker')}: {d.get('text')}" for d in panel.dialogue) or panel.action
        out_path.write_text(text + "\n", encoding="utf-8")
        return out_path


class ComicPipeline:
    def __init__(self, store: ProjectStore, llm: LLMAdapter, image_generator: ImageGenerator, animator: Animator, tts: TTSAdapter):
        self.store = store
        self.llm = llm
        self.image_generator = image_generator
        self.animator = animator
        self.tts = tts

    def generate_full_issue(self, idea: str, panel_count: int = 8, style: str = "dark ink cinematic comic") -> ComicIssue:
        issue = self.llm.write_issue(idea, panel_count, style)
        for panel in issue.panels:
            base = f"{issue.id}/{panel.id}"
            image_rel = f"{base}/panel.svg"
            audio_rel = f"{base}/dialogue.txt"
            video_rel = f"{base}/motion.txt"
            image_path = self.image_generator.generate_panel(issue, panel, self.store.asset_path(image_rel))
            audio_path = self.tts.synthesize_dialogue(issue, panel, self.store.asset_path(audio_rel))
            video_path = self.animator.animate_panel(issue, panel, image_path, self.store.asset_path(video_rel))
            panel.image_path = str(image_path.relative_to(self.store.assets_dir))
            panel.audio_path = str(audio_path.relative_to(self.store.assets_dir))
            panel.video_path = str(video_path.relative_to(self.store.assets_dir))
            panel.status = "assembled"
        self.store.save_issue(issue)
        return issue
