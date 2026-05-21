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
        self.assertIn("LIVING_COMIC_PROVIDER", text)
        self.assertIn("hapa-ltx", text)
        self.assertIn("launch-local-mlx.sh", text)
        self.assertTrue(desktop.exists())
        self.assertTrue(os.access(desktop, os.X_OK))


if __name__ == "__main__":
    unittest.main()
