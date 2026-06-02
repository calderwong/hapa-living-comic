import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from living_comic.adapters.hapa_ltx import HapaLTXAnimator, HapaLTXImageGenerator
from living_comic.providers import build_pipeline
from living_comic.storage import ProjectStore

REPO_ROOT = Path(__file__).resolve().parents[1]


class ProviderAndLauncherTests(unittest.TestCase):
    def test_hapa_ltx_provider_builds_real_local_generators(self):
        with tempfile.TemporaryDirectory() as tmp:
            pipeline = build_pipeline(ProjectStore(Path(tmp)), provider="hapa-ltx", tts_provider="mock")
            self.assertIsInstance(pipeline.image_generator, HapaLTXImageGenerator)
            self.assertIsInstance(pipeline.animator, HapaLTXAnimator)

    def test_desktop_launcher_exists_and_defaults_to_hapa_ltx(self):
        launcher = REPO_ROOT / "scripts/launch_desktop.sh"
        self.assertTrue(launcher.exists())
        self.assertTrue(os.access(launcher, os.X_OK))
        text = launcher.read_text()
        self.assertIn("HAPA_LIVING_COMIC_ROOT", text)
        self.assertIn("HAPA_LTX_NODE_ROOT", text)
        self.assertIn("LIVING_COMIC_PORT", text)
        self.assertIn("8776", text)
        self.assertIn("living-comic-book", text)
        self.assertIn("launch-local-mlx.sh", text)

    def test_swiftui_uses_dedicated_living_comic_port_and_checks_http_status(self):
        swift = REPO_ROOT / "swiftui/LivingComicBook/LivingComicBook/main.swift"
        text = swift.read_text()
        self.assertIn("http://127.0.0.1:8776", text)
        self.assertIn("HTTPURLResponse", text)
        self.assertIn("Backend HTTP", text)
        self.assertIn("timeoutIntervalForRequest = 3600", text)
        self.assertIn("@Published var panelCount = 1", text)
        self.assertIn("Generate Preview Panel", text)
        self.assertIn("panel_count\": panelCount", text)
        self.assertNotIn("http://127.0.0.1:8766", text)


if __name__ == "__main__":
    unittest.main()
