from __future__ import annotations

import os
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from living_comic.providers import build_pipeline
from living_comic.storage import ProjectStore


REPO_ROOT = Path(__file__).resolve().parents[3]
DOCS = {
    "readme": "README.md",
    "agents": "AGENTS.md",
    "feature-parity": "docs/FEATURE_PARITY.md",
}


def _doc_entry(doc_id: str, relative: str) -> dict:
    path = REPO_ROOT / relative
    return {
        "id": doc_id,
        "title": relative,
        "source": relative,
        "exists": path.exists(),
        "status": "available" if path.exists() else "DOCS MISSING",
    }


class GenerateRequest(BaseModel):
    idea: str
    panel_count: int = 8
    style: str = "dark ink cinematic comic"
    use_hermes: bool = False
    hermes_profile: str = "default"
    provider: Optional[str] = None
    tts_provider: Optional[str] = None


def create_app(data_root: Optional[Path] = None) -> FastAPI:
    app = FastAPI(title="Living Comic Book", version="0.1.0")
    app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
    store = ProjectStore(data_root or Path(os.environ.get("LIVING_COMIC_DATA", "./runtime")))
    app.mount("/assets", StaticFiles(directory=str(store.assets_dir)), name="assets")

    @app.get("/health")
    def health():
        return {"ok": True, "service": "living-comic-book", "data_root": str(store.root), "provider": os.environ.get("LIVING_COMIC_PROVIDER", "mock"), "tts_provider": os.environ.get("LIVING_COMIC_TTS_PROVIDER", "mock")}

    @app.get("/capabilities")
    def capabilities():
        return {
            "service": "living-comic-book",
            "status": "prototype",
            "surfaces": {
                "api": ["GET /health", "GET /capabilities", "GET /api/issues", "GET /api/issues/{issue_id}", "POST /api/generate", "GET /api/docs", "GET /api/docs/{doc_id}"],
                "cli": ["python3 -m living_comic.cli <idea>", "scripts/generate_mock_issue.sh <idea>", "scripts/run_backend.sh", "scripts/launch_desktop.sh"],
                "ui": ["SwiftUI macOS viewer/editor", "Docs / README sheet rendering README.md and parity docs"],
            },
            "truth": "Docs/API/CLI/UI parity is partial: generation is implemented across all three surfaces; issue listing is API-only; native UI docs viewer now exposes repo documentation through the backend whitelist.",
        }

    @app.get("/api/docs")
    def list_docs():
        return {
            "root": "hapa-living-comic",
            "docs": [_doc_entry(doc_id, relative) for doc_id, relative in DOCS.items()],
            "safety": "Markdown documents are served from a fixed allowlist only; the SwiftUI client renders Markdown text and does not execute embedded HTML or scripts.",
        }

    @app.get("/api/docs/{doc_id}")
    def get_doc(doc_id: str):
        relative = DOCS.get(doc_id)
        if not relative:
            raise HTTPException(status_code=404, detail="Unknown document id")
        path = REPO_ROOT / relative
        if not path.exists():
            raise HTTPException(status_code=404, detail=f"Document missing: {relative}")
        return {"id": doc_id, "title": relative, "source": relative, "markdown": path.read_text(encoding="utf-8")}

    @app.get("/api/issues")
    def list_issues():
        return [issue.to_dict() for issue in store.list_issues()]

    @app.get("/api/issues/{issue_id}")
    def get_issue(issue_id: str):
        try:
            return store.load_issue(issue_id).to_dict()
        except FileNotFoundError:
            raise HTTPException(status_code=404, detail="Issue not found")

    @app.post("/api/generate")
    def generate(req: GenerateRequest):
        pipeline = build_pipeline(store, use_hermes=req.use_hermes, hermes_profile=req.hermes_profile, provider=req.provider, tts_provider=req.tts_provider)
        return pipeline.generate_full_issue(req.idea, req.panel_count, req.style).to_dict()

    return app


app = create_app()
