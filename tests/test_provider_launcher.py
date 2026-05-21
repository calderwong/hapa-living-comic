import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from living_comic.adapters.hapa_ltx import HapaLTXAnimator, HapaLTXImageGenerator
from living_comic.providers import build_pipeline
from living_comic.storage import ProjectStore


class ProviderAndLauncherTests(unittest.TestCase):
    def test_hapa_ltx_provider_builds_real_local_generators(self):
        with tempfile.TemporaryDirectory() as tmp:
            pipeline = build_pipeline(ProjectStore(Path(tmp)), provider="hapa-ltx", tts_provider="mock")
            self.assertIsInstance(pipeline.image_generator, HapaLTXImageGenerator)
            self.assertIsInstance(pipeline.animator, HapaLTXAnimator)

    def test_desktop_launcher_exists_and_defaults_to_hapa_ltx(self):
        launcher = Path("/Users/calderwong/Desktop/hapa-living-comic/scripts/launch_desktop.sh")
        desktop = Path("/Users/calderwong/Desktop/Hapa Living Comic.command")
        self.assertTrue(launcher.exists())
        self.assertTrue(os.access(launcher, os.X_OK))
        text = launcher.read_text()
        self.assertIn("LIVING_COMIC_PORT", text)
        self.assertIn("8776", text)
        self.assertIn("living-comic-book", text)
        self.assertIn("launch-local-mlx.sh", text)
        self.assertTrue(desktop.exists())
        self.assertTrue(os.access(desktop, os.X_OK))

    def test_swiftui_uses_dedicated_living_comic_port_and_checks_http_status(self):
        swift = Path("/Users/calderwong/Desktop/hapa-living-comic/swiftui/LivingComicBook/LivingComicBook/main.swift")
        text = swift.read_text()
        self.assertIn("http://127.0.0.1:8776", text)
        self.assertIn("HTTPURLResponse", text)
        self.assertIn("Backend HTTP", text)
        self.assertNotIn("http://127.0.0.1:8766", text)


if __name__ == "__main__":
    unittest.main()
