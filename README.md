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
cd "$HAPA_LIVING_COMIC_ROOT"
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

A one-click launcher can point at this repo and the local Hapa LTX Node:

```text
$HAPA_LIVING_COMIC_DESKTOP_LAUNCHER
```

Double-click it to:

1. ensure the Hapa LTX Node is running at `http://127.0.0.1:8753`, using `$HAPA_LTX_NODE_ROOT/scripts/launch-local-mlx.sh`;
2. start this app's backend at `http://127.0.0.1:8776` with `LIVING_COMIC_PROVIDER=hapa-ltx` and `LIVING_COMIC_TTS_PROVIDER=mac-say`;
3. launch the SwiftUI viewer.

Logs go to:

```text
$HAPA_LIVING_COMIC_ROOT/logs
```

## Real local generator mode

With the Hapa LTX Node already running:

```bash
cd "$HAPA_LIVING_COMIC_ROOT"
export PYTHONPATH=backend
export LIVING_COMIC_PROVIDER=hapa-ltx
export LIVING_COMIC_TTS_PROVIDER=mac-say
export HAPA_LTX_URL=http://127.0.0.1:8753
export HAPA_LTX_NODE_ROOT=/path/to/hapa-ltx-node
export HAPA_LTX_TOKEN_FILE="$HAPA_LTX_NODE_ROOT/.node_token"
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
cd "$HAPA_LIVING_COMIC_ROOT/swiftui/LivingComicBook"
swift run
```

Click **Generate Full Issue**. Click panels to activate/zoom the layout.

The primary shell also includes **Docs / README** (`⌘?`), which opens the in-app Markdown reader. The reader loads repo docs from the backend allowlist (`README.md`, `AGENTS.md`, `docs/FEATURE_PARITY.md`), shows source/provenance paths, renders Markdown with SwiftUI text, and labels missing docs as `DOCS MISSING` instead of showing a blank panel.

## Node-app compliance and parity

This is an active Hapa prototype node app with partial-but-truthful API / CLI / UI parity:

- API: backend health, capabilities, issue generation/list/read, asset serving, and whitelisted docs endpoints.
- CLI: `python3 -m living_comic.cli`, `scripts/generate_mock_issue.sh`, `scripts/run_backend.sh`, and `scripts/launch_desktop.sh`.
- UI: native SwiftUI viewer/editor, media playback, generation controls, status/error text, and in-app Docs / README Markdown surface.

See `AGENTS.md` for AI-agent operating context and `docs/FEATURE_PARITY.md` for the capability-by-capability parity matrix, verification notes, and caveats. Current compliance state: **partial verified prototype**; real Hapa LTX generation remains dependent on the external local Hapa LTX Node.

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


### Shared ecosystem pattern

Hapa is built as a constellation of modular nodes. Each node owns a focused capability, but participates in a shared protocol for provenance, handoff, cards, memory, and operations.

Every node is designed for both human operators and AI agents. The target contract is three surfaces: a UI for direct human review/control, an API for node-to-node and agent calls, and a CLI for scripted runs, audits, and handoffs. Individual repos may be at different maturity levels, but the public contract is that humans and agents can inspect, operate, and verify the node.

Hapa nodes power AI agents and avatar-agents that build new nodes and enhance existing ones. As work moves through the ecosystem, it is mined for utility, wisdom, and repeatable logic, then distilled into Hapa Cards: portable packets of skills, context, memories, and operational patterns.

Humans and AIs use Hapa Cards to discuss, ideate, prototype, and deploy increasingly complex workflows through a playable, card-collecting mechanic. Collaboration history, skills, work artifacts, and canonical decisions are stored in [hapa-second-brain](https://github.com/calderwong/hapa-second-brain), enriched into [Hapa Worldbuilding Wiki](https://github.com/calderwong/hapa-worldbuilding-wiki) entries, and converted back into cards. Avatar-agents can also be combined or specialized into purpose-built identities with their own storage, lore, canon, card decks, skills, and protocols.

### Purpose

SwiftUI/native comic viewer/editor prototype for Hapa narrative panels, runtime comic surfaces, and media-backed story presentation.

### Current status

- Status: **prototype narrative app**.
- Local source root: `$HAPA_LIVING_COMIC_ROOT`.
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

- [hapa-dev-proto](https://github.com/calderwong/hapa-dev-proto-private) — Primary local-first app; many nodes feed it cards, assets, chat, debug, or projection data.
- [Hapa_Worldbuilding_Wiki](https://github.com/calderwong/hapa-worldbuilding-wiki) — Canonical Markdown graph for lore, nodes, names, cards, systems, and provenance.
- [.Overwatch](https://github.com/calderwong/overwatch) — Operations map: inventory, source index, task inbox, protocols, and runbooks.
- [hapa-telemetry-node](https://github.com/calderwong/hapa-telemetry-node) — Discovery/monitoring hub for node health, capabilities, launchers, and relationships.
- [hapa-keys-node](https://github.com/calderwong/hapa-keys-node) — Local key vault used by authenticated nodes and tools.
- [hapa-lore-node](https://github.com/calderwong/hapa-lore-node) — Chronicle/canon service for daily progress, lore, and searchable wisdom.
- [hapa-anvil-node](https://github.com/calderwong/hapa-anvil-node) — Card standardization/evaluation/forge node for turning raw card ideas into usable artifacts.
- [hapa-janus-world-node](https://github.com/calderwong/hapa-janus-world-node) — World-state truth kernel and event tape for Janus/desktop simulation work.
- [hapa-mlx-station](https://github.com/calderwong/hapa-mlx-station) — Apple Silicon media-generation station that produces visual/audio assets for cards, wiki, and production runs.
- [hapa-lance-node](https://github.com/calderwong/hapa-lance-node) — Local indexing/projection layer for cards, wiki chunks, embeddings, and multimodal records.

### Operating contract

- Treat generated media, local databases, model weights, dependency folders, build outputs, app bundles, and secrets as runtime artifacts unless this README explicitly says otherwise.
- Prefer loopback/local operation first; expose network services only with explicit auth and operator intent.
- When this node produces artifacts for another node, record enough provenance for the receiving node or wiki page to recover the source path, command, prompt, or API request.
- Keep `README.md`, `LICENSE`, `NOTICE.md` where applicable, and repo-local screenshots current as the node evolves.
