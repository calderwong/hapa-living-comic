from __future__ import annotations

import json
import os
import shutil
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any, Dict, Optional

from living_comic.models import ComicIssue, ComicPanel


class HapaLTXNodeClient:
    """Small HTTP client for the local Hapa LTX Node.

    The node exposes:
      POST /v1/jobs
      GET  /v1/jobs/{id}
      GET  /v1/artifacts/{job_id}/{name}

    Tokens are read from HAPA_LTX_TOKEN or the node's .node_token file. The token is
    only used in the Authorization header and is never printed by this module.
    """

    def __init__(
        self,
        base_url: Optional[str] = None,
        token: Optional[str] = None,
        token_file: Optional[Path] = None,
        poll_interval: float = 1.0,
        timeout: float = 900.0,
    ):
        self.base_url = (base_url or os.environ.get("HAPA_LTX_URL") or "http://127.0.0.1:8753").rstrip("/")
        self.token = token or os.environ.get("HAPA_LTX_TOKEN") or self._read_token(token_file)
        self.poll_interval = poll_interval
        self.timeout = timeout

    def _read_token(self, token_file: Optional[Path]) -> str:
        candidates = []
        if token_file:
            candidates.append(Path(token_file))
        env_file = os.environ.get("HAPA_LTX_TOKEN_FILE")
        if env_file:
            candidates.append(Path(env_file).expanduser())
        node_root = os.environ.get("HAPA_LTX_NODE_ROOT")
        if node_root:
            candidates.append(Path(node_root).expanduser() / ".node_token")
        for path in candidates:
            try:
                if path.exists():
                    return path.read_text(encoding="utf-8").strip()
            except OSError:
                continue
        return ""

    def auth_header(self) -> Dict[str, str]:
        headers = {"Content-Type": "application/json"}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        return headers

    def health(self) -> Dict[str, Any]:
        return self._request("GET", "/health")

    def submit_and_wait(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        job = self._request("POST", "/v1/jobs", payload)
        job_id = job.get("id")
        if not job_id:
            raise RuntimeError(f"Hapa LTX Node returned no job id: {job}")
        deadline = time.time() + self.timeout
        while True:
            current = self._request("GET", f"/v1/jobs/{job_id}")
            status = current.get("status")
            if status == "succeeded":
                return current
            if status in {"failed", "cancelled"}:
                raise RuntimeError(f"Hapa LTX job {job_id} ended as {status}: {current.get('error')}")
            if time.time() > deadline:
                raise TimeoutError(f"Timed out waiting for Hapa LTX job {job_id}")
            time.sleep(self.poll_interval)

    def copy_artifact(self, job: Dict[str, Any], out_path: Path) -> Path:
        out_path.parent.mkdir(parents=True, exist_ok=True)
        artifact_path = job.get("artifact_path")
        if artifact_path and Path(artifact_path).exists():
            shutil.copyfile(artifact_path, out_path)
            return out_path
        artifact_url = job.get("artifact_url")
        if not artifact_url:
            raise RuntimeError(f"Job has no artifact path/url: {job}")
        data = self._request_bytes("GET", artifact_url)
        out_path.write_bytes(data)
        return out_path

    def _request(self, method: str, path: str, body: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        data = None if body is None else json.dumps(body).encode("utf-8")
        req = urllib.request.Request(f"{self.base_url}{path}", data=data, method=method, headers=self.auth_header())
        try:
            with urllib.request.urlopen(req, timeout=30) as res:
                return json.loads(res.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")
            raise RuntimeError(f"Hapa LTX Node HTTP {exc.code} on {method} {path}: {detail}") from exc
        except urllib.error.URLError as exc:
            raise RuntimeError(f"Cannot reach Hapa LTX Node at {self.base_url}: {exc.reason}") from exc

    def _request_bytes(self, method: str, path: str) -> bytes:
        req = urllib.request.Request(f"{self.base_url}{path}", method=method, headers=self.auth_header())
        with urllib.request.urlopen(req, timeout=60) as res:
            return res.read()


def _panel_prompt(issue: ComicIssue, panel: ComicPanel) -> str:
    parts = [
        issue.style,
        panel.visual_prompt,
        panel.composition,
        panel.lighting,
        panel.emotion,
        f"Action: {panel.action}",
        "dark polished living comic book panel, clean gutters, strong silhouette, speech bubble safe space",
    ]
    return ", ".join(p for p in parts if p)


class HapaLTXImageGenerator:
    def __init__(
        self,
        client: Optional[HapaLTXNodeClient] = None,
        backend: str = "z_image_mflux",
        width: int = 1024,
        height: int = 1024,
        image_steps: int = 9,
        image_guidance: float = 0,
    ):
        self.client = client or HapaLTXNodeClient(timeout=float(os.environ.get("HAPA_LTX_IMAGE_TIMEOUT", "900")))
        self.backend = os.environ.get("HAPA_LTX_IMAGE_BACKEND") or backend
        self.width = int(os.environ.get("HAPA_LTX_IMAGE_WIDTH", width))
        self.height = int(os.environ.get("HAPA_LTX_IMAGE_HEIGHT", height))
        self.image_steps = int(os.environ.get("HAPA_LTX_IMAGE_STEPS", image_steps))
        self.image_guidance = float(os.environ.get("HAPA_LTX_IMAGE_GUIDANCE", image_guidance))

    def generate_panel(self, issue: ComicIssue, panel: ComicPanel, out_path: Path) -> Path:
        if out_path.suffix.lower() != ".png":
            out_path = out_path.with_suffix(".png")
        payload = {
            "mode": "text-to-image",
            "prompt": _panel_prompt(issue, panel),
            "negative_prompt": "blurry, low quality, unreadable text, bad anatomy, flicker",
            "backend": self.backend,
            "width": self.width,
            "height": self.height,
            "image_steps": self.image_steps,
            "image_guidance": self.image_guidance,
            "project": "hapa-living-comic",
            "tags": ["living-comic", issue.id, panel.id],
        }
        job = self.client.submit_and_wait(payload)
        return self.client.copy_artifact(job, out_path)


class HapaLTXAnimator:
    def __init__(
        self,
        client: Optional[HapaLTXNodeClient] = None,
        backend: str = "local_mlx",
        width: int = 384,
        height: int = 256,
        seconds: float = 1.0,
        fps: int = 24,
        seed: int = 123,
    ):
        self.client = client or HapaLTXNodeClient(timeout=float(os.environ.get("HAPA_LTX_VIDEO_TIMEOUT", "1200")))
        self.backend = os.environ.get("HAPA_LTX_VIDEO_BACKEND") or backend
        self.width = int(os.environ.get("HAPA_LTX_VIDEO_WIDTH", width))
        self.height = int(os.environ.get("HAPA_LTX_VIDEO_HEIGHT", height))
        self.seconds = float(os.environ.get("HAPA_LTX_VIDEO_SECONDS", seconds))
        self.fps = int(os.environ.get("HAPA_LTX_VIDEO_FPS", fps))
        self.seed = int(os.environ.get("HAPA_LTX_VIDEO_SEED", seed))

    def animate_panel(self, issue: ComicIssue, panel: ComicPanel, image_path: Path, out_path: Path) -> Path:
        if out_path.suffix.lower() != ".mp4":
            out_path = out_path.with_suffix(".mp4")
        payload = {
            "mode": "image-to-video",
            "prompt": f"{_panel_prompt(issue, panel)}. Motion: {panel.camera or 'subtle parallax, cinematic push-in'}. Keep composition coherent.",
            "negative_prompt": "flicker, melting, low quality, warped faces, unstable text",
            "backend": self.backend,
            "source_image": str(image_path),
            "width": self.width,
            "height": self.height,
            "seconds": self.seconds,
            "fps": self.fps,
            "seed": self.seed,
            "project": "hapa-living-comic",
            "tags": ["living-comic", issue.id, panel.id, "ltx-2.3"],
        }
        job = self.client.submit_and_wait(payload)
        return self.client.copy_artifact(job, out_path)
