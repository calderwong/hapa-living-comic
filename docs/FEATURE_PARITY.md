# Hapa Living Comic Book — Feature Parity

Status: partial protocol compliance after the 2026-05-26 healing pass.

This repo is an active Hapa prototype node app. It has a Python backend feature spine, CLI generation path, native SwiftUI UI, and a built-in UI docs reader. It is not yet a fully complete production node because some capabilities are API-only or depend on local media services.

## Capability parity matrix

| Capability | API | CLI | UI | Data source | Auth | Verification | Status |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Health/status | `GET /health` | `scripts/run_backend.sh` then curl | backend status appears indirectly through generate/docs errors | local process/env | loopback only | unit/API smoke, curl | partial |
| Capability manifest | `GET /capabilities` | curl/manual | summarized in Docs/README docs | static manifest in `server.py` | loopback only | API smoke | partial |
| Generate living comic issue | `POST /api/generate` | `python3 -m living_comic.cli <idea>` and `scripts/generate_mock_issue.sh` | Generate Preview Panel / Generate Issue button | `ProjectStore`, mock/Hapa LTX providers, optional Hermes | loopback only; Hapa LTX token external | unit tests and optional live smoke | verified prototype |
| List/load saved issues | `GET /api/issues`, `GET /api/issues/{issue_id}` | not exposed as a dedicated CLI command yet | generated issue only in current session | runtime issue JSON | loopback only | storage/API tests | partial |
| Serve generated media assets | `GET /assets/...` | file paths under runtime | SwiftUI `AsyncImage` / `VideoPlayer` | runtime assets dir | loopback only | `test_asset_viewer.py` | verified prototype |
| README / Markdown docs viewer | `GET /api/docs`, `GET /api/docs/{doc_id}` from whitelist | curl/manual | `Docs / README` button opens native Markdown renderer with source/provenance and missing-doc status | `README.md`, `AGENTS.md`, `docs/FEATURE_PARITY.md` | loopback only | docs endpoint tests and `swift build` | verified prototype |

## UI documentation reader standard

The SwiftUI shell now exposes `Docs / README` in the primary sidebar. It opens a docs sheet that:

- loads `/api/docs` from the backend;
- renders `README.md` by default;
- lists `AGENTS.md` and `docs/FEATURE_PARITY.md` when present;
- shows source/provenance paths;
- labels missing documents as `DOCS MISSING` instead of blank content;
- uses SwiftUI Markdown text rendering from a fixed backend allowlist rather than executing arbitrary HTML/scripts.

## Known caveats

- This pass verifies build/test compliance, not a full interactive macOS UI screenshot smoke.
- Real Hapa LTX mode still depends on the external local Hapa LTX Node and token file.
- Issue listing is not yet exposed as a first-class UI library browser or CLI subcommand.
- `/capabilities` is a truthful manifest, not a dynamic service registry.

## Recommended next increments

1. Add CLI subcommands for `list-issues`, `show-issue`, and `docs` if this app becomes an operator tool rather than a one-shot generator.
2. Add a UI issue library/browser backed by `GET /api/issues`.
3. Add a live UI smoke script or screenshot harness for the SwiftUI Docs sheet when a GUI session is available.
