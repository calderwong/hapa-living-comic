# Hapa Living Comic Book

Local-first prototype for a beautiful Living Comic Book desktop app.

The prototype is intentionally end-to-end with mock providers first, so the app works before wiring expensive/local generative nodes. The provider interfaces are ready for:

- Hermes/Qwen/Mistral script generation
- custom image generation node / ComfyUI workflow
- LTX 2.3 image-to-video animation
- MimikaStudio / Qwen3-TTS / mlx-audio voice cloning

## Folder structure

```text
backend/living_comic/      Python pipeline, storage, API, adapters
swiftui/LivingComicBook/   SwiftUI macOS viewer/editor shell
tests/                     unittest coverage for project storage + pipeline
scripts/                   run helpers
docs/plans/                implementation plan
runtime/                   generated local projects/assets (created at runtime)
```

## Run backend

```bash
cd /Users/calderwong/Desktop/hapa-living-comic
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
scripts/run_backend.sh
```

Health check:

```bash
curl http://127.0.0.1:8766/health
```

Generate a mock issue:

```bash
scripts/generate_mock_issue.sh "Calder, Thor, and the Huemon Trainer build a living comic"
```

Generate through API:

```bash
curl -X POST http://127.0.0.1:8766/api/generate   -H 'Content-Type: application/json'   -d '{"idea":"A Hapa campfire becomes a living comic","panel_count":6}'
```

## Run SwiftUI viewer

In a second terminal, with backend running:

```bash
cd /Users/calderwong/Desktop/hapa-living-comic/swiftui/LivingComicBook
swift run
```

Click **Generate Full Issue**. Click panels to activate/zoom the layout.

## Hermes integration

Backend `HermesLLM` can call Hermes directly:

```bash
curl -X POST http://127.0.0.1:8766/api/generate   -H 'Content-Type: application/json'   -d '{"idea":"Continue this comic with Thor interrupting the trainer","panel_count":8,"use_hermes":true,"hermes_profile":"mtplxqwen36"}'
```

From Hermes, you can control it with local HTTP commands once the backend is running.

Future deeper integration options:

- Add a Hermes MCP server exposing `generate_issue`, `regenerate_panel`, `export_video`.
- Add Hermes webhook routes for “continue this comic”.
- Add a repo skill documenting this app workflow after the first full local-node integration succeeds.

## Local node integration points

- Image generation: `backend/living_comic/adapters/comfy_image.py`
- LTX 2.3: `backend/living_comic/adapters/ltx23.py`
- Voice cloning: `backend/living_comic/adapters/tts.py`

Right now those are safe adapters/placeholders because this environment did not expose a running ComfyUI server, Hyperframes CLI, LTX command, MimikaStudio, Qwen3-TTS, or mlx-audio command during the initial scaffold.

## Tests

```bash
PYTHONPATH=backend python3 -m unittest discover -s tests
```
