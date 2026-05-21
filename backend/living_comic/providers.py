from __future__ import annotations

import os
from pathlib import Path
from typing import Tuple

from living_comic.adapters.hapa_ltx import HapaLTXAnimator, HapaLTXImageGenerator
from living_comic.adapters.tts import LocalCommandVoiceCloneTTS, MacSayTTS
from living_comic.pipeline import (
    ComicPipeline,
    HermesLLM,
    MockImageGenerator,
    MockLLM,
    MockLTXAnimator,
    MockTTS,
)
from living_comic.storage import ProjectStore


def build_pipeline(
    store: ProjectStore,
    use_hermes: bool = False,
    hermes_profile: str = "default",
    provider: str | None = None,
    tts_provider: str | None = None,
) -> ComicPipeline:
    """Build a pipeline from explicit request values plus environment defaults.

    LIVING_COMIC_PROVIDER:
      mock       -> mock image/video/TTS
      hapa-ltx   -> Hapa LTX Node for images and image-to-video

    LIVING_COMIC_TTS_PROVIDER:
      mock      -> text placeholder
      mac-say   -> macOS local say command
      command   -> local voice-clone command template via LIVING_COMIC_TTS_CMD
    """

    provider = (provider or os.environ.get("LIVING_COMIC_PROVIDER") or "mock").strip().lower()
    tts_provider = (tts_provider or os.environ.get("LIVING_COMIC_TTS_PROVIDER") or ("mac-say" if provider == "hapa-ltx" else "mock")).strip().lower()
    llm = HermesLLM(hermes_profile) if use_hermes else MockLLM()

    if provider in {"hapa-ltx", "hapa_ltx", "real"}:
        image_generator = HapaLTXImageGenerator()
        animator = HapaLTXAnimator()
    elif provider == "mock":
        image_generator = MockImageGenerator()
        animator = MockLTXAnimator()
    else:
        raise ValueError(f"Unknown LIVING_COMIC_PROVIDER/provider: {provider}")

    if tts_provider in {"mac-say", "say"}:
        tts = MacSayTTS()
    elif tts_provider in {"command", "voice-clone", "voiceclone"}:
        tts = LocalCommandVoiceCloneTTS()
    elif tts_provider == "mock":
        tts = MockTTS()
    else:
        raise ValueError(f"Unknown LIVING_COMIC_TTS_PROVIDER/tts_provider: {tts_provider}")

    return ComicPipeline(store, llm, image_generator, animator, tts)
