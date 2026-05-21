import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from living_comic.adapters.hapa_ltx import HapaLTXAnimator, HapaLTXImageGenerator, HapaLTXNodeClient
from living_comic.models import ComicIssue, ComicPanel


class FakeClient(HapaLTXNodeClient):
    def __init__(self):
        super().__init__(base_url="http://ltx.local", token="test-token", poll_interval=0, timeout=1)
        self.jobs = []

    def submit_and_wait(self, payload):
        self.jobs.append(payload)
        suffix = ".png" if payload["mode"] == "text-to-image" else ".mp4"
        out = Path(tempfile.mkdtemp()) / f"artifact{suffix}"
        out.write_bytes(b"artifact")
        return {"id": "job-1", "status": "succeeded", "artifact_path": str(out)}


class HapaLTXAdapterTests(unittest.TestCase):
    def issue_panel(self):
        issue = ComicIssue(id="issue-1", title="Test", logline="", style="ink")
        panel = ComicPanel(id="panel-1", page=1, panel=1, action="Calder opens the comic.", visual_prompt="cinematic Hapa panel", camera="slow push")
        return issue, panel

    def test_image_generator_posts_text_to_image_payload_and_copies_artifact(self):
        client = FakeClient()
        issue, panel = self.issue_panel()
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "panel.png"
            result = HapaLTXImageGenerator(client=client).generate_panel(issue, panel, out)
            self.assertEqual(result, out)
            self.assertEqual(out.read_bytes(), b"artifact")
        self.assertEqual(client.jobs[0]["mode"], "text-to-image")
        self.assertEqual(client.jobs[0]["backend"], "z_image_mflux")
        self.assertIn("cinematic Hapa panel", client.jobs[0]["prompt"])

    def test_animator_posts_image_to_video_payload_and_copies_artifact(self):
        client = FakeClient()
        issue, panel = self.issue_panel()
        with tempfile.TemporaryDirectory() as tmp:
            image = Path(tmp) / "panel.png"
            image.write_bytes(b"image")
            out = Path(tmp) / "panel.mp4"
            result = HapaLTXAnimator(client=client).animate_panel(issue, panel, image, out)
            self.assertEqual(result, out)
            self.assertEqual(out.read_bytes(), b"artifact")
        self.assertEqual(client.jobs[0]["mode"], "image-to-video")
        self.assertEqual(client.jobs[0]["backend"], "local_mlx")
        self.assertEqual(client.jobs[0]["source_image"], str(image))

    def test_client_reads_token_from_file_without_logging_secret(self):
        with tempfile.TemporaryDirectory() as tmp:
            token_file = Path(tmp) / ".node_token"
            token_file.write_text("secret-token\n")
            client = HapaLTXNodeClient(base_url="http://127.0.0.1:8753", token_file=token_file)
            self.assertEqual(client.auth_header()["Authorization"], "Bearer secret-token")


if __name__ == "__main__":
    unittest.main()
