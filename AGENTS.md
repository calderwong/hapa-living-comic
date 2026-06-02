# Hapa Living Comic Book — Agent Guide

This repo is an active Hapa prototype node app. Treat it as a local-first narrative/media app, not as a finished production service.

## Source of truth

- `README.md` — human quickstart, operating context, and current caveats.
- `docs/FEATURE_PARITY.md` — API / CLI / UI parity matrix and verification state.
- `backend/living_comic/` — Python feature spine, API, providers, storage, adapters.
- `swiftui/LivingComicBook/LivingComicBook/main.swift` — native macOS SwiftUI viewer/editor shell.
- `tests/` — Python unit/API smoke coverage.

## Safe edit boundaries

- Prefer changes inside this repo root. Use `$HAPA_LIVING_COMIC_ROOT` when a script or doc needs a concrete local root.
- Runtime issue output belongs under `runtime/` and should remain out of git unless deliberately promoted as a fixture.
- Generated logs/build folders (`logs/`, `.build/`, virtualenvs) are runtime artifacts.
- Do not hard-code secrets or Hapa LTX Node tokens; use `HAPA_LTX_TOKEN_FILE` or local env.

## Interface contract

Core living-comic generation is exposed through:

- API: `POST /api/generate`, `GET /health`, `GET /capabilities`, issue reads, and docs endpoints.
- CLI: `python3 -m living_comic.cli <idea>` plus helper scripts under `scripts/`.
- UI: SwiftUI macOS viewer/editor with media display and a `Docs / README` sheet that loads repo Markdown through the backend whitelist.

Parity is partial by design while this remains a prototype. Do not claim full compliance unless `docs/FEATURE_PARITY.md` has been updated and tests/smokes prove it.

## Verification gates

Run at minimum:

```bash
cd "$HAPA_LIVING_COMIC_ROOT"
PYTHONPATH=backend python3 -m unittest discover -s tests
cd swiftui/LivingComicBook && swift build
```

Optional live smoke when the backend can run:

```bash
scripts/run_backend.sh
curl http://127.0.0.1:8776/health
curl http://127.0.0.1:8776/capabilities
curl http://127.0.0.1:8776/api/docs/readme
```

## Known pitfalls

- The real Hapa LTX provider depends on a local node at `http://127.0.0.1:8753` and may be slow; use mock mode for fast tests.
- The SwiftUI viewer expects the backend at `LIVING_COMIC_BACKEND_URL` or `http://127.0.0.1:8776`.
- The docs viewer intentionally serves only whitelisted Markdown files; do not replace it with arbitrary filesystem reads.
- If adding new capabilities, update API, CLI, UI, README, tests, and `docs/FEATURE_PARITY.md` together or mark the missing surfaces truthfully.
