# Hapa Living Comic Book

Local-first prototype for a beautiful Living Comic Book desktop app.

The prototype supports an end-to-end mock mode plus a real local-node mode for the Hapa LTX Node.

Provider interfaces are wired for:

- Hermes/Qwen/Mistral script generation
- Hapa LTX Node text-to-image via `z_image_mflux`
- Hapa LTX Node LTX 2.3 image-to-video via `local_mlx`
- local macOS `say` TTS now; command-template voice cloning once MimikaStudio/Qwen3-TTS/mlx-audio command is provided

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
curl http://127.0.0.1:8776/health
```

Generate a mock issue:

```bash
scripts/generate_mock_issue.sh "Calder, Thor, and the Huemon Trainer build a living comic"
```

Generate through API:

```bash
curl -X POST http://127.0.0.1:8776/api/generate   -H 'Content-Type: application/json'   -d '{"idea":"A Hapa campfire becomes a living comic","panel_count":6}'
```

## Desktop launcher

A one-click launcher was created at:

```text
/Users/calderwong/Desktop/Hapa Living Comic.command
```

Double-click it to:

1. ensure the Hapa LTX Node is running at `http://127.0.0.1:8753`, using `/Users/calderwong/Documents/Codex/2026-05-19/thoroughly-review-the-hapa-worldbuilding-wiki/hapa-ltx-node/scripts/launch-local-mlx.sh`;
2. start this app's backend at `http://127.0.0.1:8776` with `LIVING_COMIC_PROVIDER=hapa-ltx` and `LIVING_COMIC_TTS_PROVIDER=mac-say`;
3. launch the SwiftUI viewer.

Logs go to:

```text
/Users/calderwong/Desktop/hapa-living-comic/logs
```

## Real local generator mode

With the Hapa LTX Node already running:

```bash
cd /Users/calderwong/Desktop/hapa-living-comic
export PYTHONPATH=backend
export LIVING_COMIC_PROVIDER=hapa-ltx
export LIVING_COMIC_TTS_PROVIDER=mac-say
export HAPA_LTX_URL=http://127.0.0.1:8753
export HAPA_LTX_TOKEN_FILE="/Users/calderwong/Documents/Codex/2026-05-19/thoroughly-review-the-hapa-worldbuilding-wiki/hapa-ltx-node/.node_token"
python3 -m living_comic.cli "Calder and Thor open the living comic engine" --provider hapa-ltx --tts-provider mac-say --panels 1
```

Image settings can be tuned with:

```bash
export HAPA_LTX_IMAGE_BACKEND=z_image_mflux
export HAPA_LTX_IMAGE_WIDTH=1024
export HAPA_LTX_IMAGE_HEIGHT=1024
export HAPA_LTX_IMAGE_STEPS=9
```

Video settings can be tuned with:

```bash
export HAPA_LTX_VIDEO_BACKEND=local_mlx
export HAPA_LTX_VIDEO_WIDTH=384
export HAPA_LTX_VIDEO_HEIGHT=256
export HAPA_LTX_VIDEO_SECONDS=1
export HAPA_LTX_VIDEO_FPS=24
```

For voice cloning, set a command template instead of macOS `say`:

```bash
export LIVING_COMIC_TTS_PROVIDER=command
export LIVING_COMIC_VOICE_REFERENCE=/path/to/calder-reference.wav
export LIVING_COMIC_TTS_CMD='mlx-audio tts --text {text_json} --ref {reference_clip} --output {out}'
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
curl -X POST http://127.0.0.1:8776/api/generate   -H 'Content-Type: application/json'   -d '{"idea":"Continue this comic with Thor interrupting the trainer","panel_count":8,"use_hermes":true,"hermes_profile":"mtplxqwen36"}'
```

From Hermes, you can control it with local HTTP commands once the backend is running.

Future deeper integration options:

- Add a Hermes MCP server exposing `generate_issue`, `regenerate_panel`, `export_video`.
- Add Hermes webhook routes for “continue this comic”.
- Add a repo skill documenting this app workflow after the first full local-node integration succeeds.

## Local node integration points

- Hapa LTX Node adapter: `backend/living_comic/adapters/hapa_ltx.py`
- TTS adapters: `backend/living_comic/adapters/tts.py`
- Provider selection factory: `backend/living_comic/providers.py`
- Legacy/alternate Comfy adapter stub: `backend/living_comic/adapters/comfy_image.py`
- Legacy/alternate generic LTX adapter stub: `backend/living_comic/adapters/ltx23.py`

Hyperframes/Codex note: this Hermes environment did not expose a `codex` binary, `hyperframes` CLI, or installed Hermes-visible hyperframes skill. The app is therefore wired directly to the Hapa LTX Node as requested. A future Hyperframes adapter can call the same saved issue JSON and panel asset paths once the Codex-side skill/CLI is exposed here.

## Tests

```bash
PYTHONPATH=backend python3 -m unittest discover -s tests
```


<!-- HAPA-README-QUALITY-PASS-2026-05-22 -->

## Hapa ecosystem context

### Purpose

SwiftUI/native comic viewer/editor prototype for Hapa narrative panels, runtime comic surfaces, and media-backed story presentation.

### Current status

- Status: **prototype narrative app**.
- Local source root: `/Users/calderwong/Desktop/hapa-living-comic`.
- This README is intended to be useful to both human operators and future agents: it should explain what the node is for, what it consumes, what it emits, how it connects to other Hapa nodes, and what should stay out of git.

### Inputs

- Comic panel assets, script/narrative data, local runtime state, generated media

### Outputs

- Native comic viewer/editor experience, panel previews, and presentation-ready narrative surfaces

### Interfaces

- SwiftUI app source
- Runtime panel/image assets
- Native macOS/iOS build flow

### Related Hapa nodes

- [Hapa AG / Dev Proto](file:///Users/calderwong/Desktop/hapa-dev-proto) — Primary local-first app; many nodes feed it cards, assets, chat, debug, or projection data.
- [Hapa Worldbuilding Wiki](file:///Users/calderwong/Desktop/Hapa_Worldbuilding_Wiki) — Canonical Markdown graph for lore, nodes, names, cards, systems, and provenance.
- [Overwatch](file:///Users/calderwong/Desktop/.Overwatch) — Operations map: inventory, source index, task inbox, protocols, and runbooks.
- [Hapa Telemetry Node](file:///Users/calderwong/Desktop/hapa-telemetry-node) — Discovery/monitoring hub for node health, capabilities, launchers, and relationships.
- [Hapa Keys Node](file:///Users/calderwong/Desktop/hapa-keys-node) — Local key vault used by authenticated nodes and tools.
- [Hapa Lore Node](file:///Users/calderwong/Desktop/hapa-lore-node) — Chronicle/canon service for daily progress, lore, and searchable wisdom.
- [Hapa Anvil Node](file:///Users/calderwong/Desktop/hapa-anvil-node) — Card standardization/evaluation/forge node for turning raw card ideas into usable artifacts.
- [Hapa Janus World Node](file:///Users/calderwong/Desktop/hapa-janus-world-node) — World-state truth kernel and event tape for Janus/desktop simulation work.
- [Hapa MLX Station](file:///Users/calderwong/hapa-mlx-station) — Apple Silicon media-generation station that produces visual/audio assets for cards, wiki, and production runs.
- [Hapa Lance Node](file:///Users/calderwong/Desktop/hapa-lance-node) — Local indexing/projection layer for cards, wiki chunks, embeddings, and multimodal records.

### Operating contract

- Treat generated media, local databases, model weights, dependency folders, build outputs, app bundles, and secrets as runtime artifacts unless this README explicitly says otherwise.
- Prefer loopback/local operation first; expose network services only with explicit auth and operator intent.
- When this node produces artifacts for another node, record enough provenance for the receiving node or wiki page to recover the source path, command, prompt, or API request.
- Keep `README.md`, `LICENSE`, `NOTICE.md` where applicable, and repo-local screenshots current as the node evolves.
