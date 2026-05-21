# Living Comic Book Prototype Implementation Plan

> **For Hermes:** Use subagent-driven-development skill to implement this plan task-by-task.

**Goal:** Build a local-first desktop prototype that turns an idea into a scripted, panel-based living comic with generated assets and an editor/viewer shell.

**Architecture:** Python FastAPI backend owns project storage and pipeline orchestration. A SwiftUI frontend calls the backend, displays panels in a comic layout, and later plays panel-specific image/video/audio assets. Provider adapters isolate Hermes/LLM scripting, custom image generation, LTX 2.3 animation, and local voice cloning.

**Tech Stack:** Python 3.9+, FastAPI, filesystem JSON/assets, SwiftUI macOS, Hermes CLI profile integration, Comfy/custom image node adapter, LTX 2.3 adapter placeholder, local TTS adapter.

---

## Milestones

1. Working mock end-to-end: idea -> issue JSON -> SVG placeholders -> mock audio/video placeholders -> SwiftUI display.
2. Hermes-backed script generation: `use_hermes=true` calls `hermes chat -p <profile>`.
3. Custom image node: fill `ComfyUIImageGenerator.generate_panel` with workflow mapping.
4. Voice cloning: fill `VoiceCloneTTS` for MimikaStudio/Qwen3-TTS/mlx-audio once the reference clip and command/API are known.
5. LTX 2.3: fill `LTX23Animator` with image-to-video workflow submit/poll/download.
6. Editor: regenerate panel, edit prompts/dialogue, re-voice line, export stitched video.
