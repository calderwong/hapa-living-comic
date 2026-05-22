import tempfile
import unittest
from pathlib import Path

from fastapi.testclient import TestClient

from living_comic.api.server import create_app


class AssetServingTests(unittest.TestCase):
    def test_assets_are_served_over_http_for_swiftui_viewer(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            asset = root / "assets" / "issue-demo" / "panel-1" / "panel.svg"
            asset.parent.mkdir(parents=True)
            asset.write_text("<svg xmlns='http://www.w3.org/2000/svg'></svg>", encoding="utf-8")
            client = TestClient(create_app(root))
            response = client.get("/assets/issue-demo/panel-1/panel.svg")
            self.assertEqual(response.status_code, 200)
            self.assertIn("svg", response.text)

    def test_swiftui_renders_media_assets_not_text_only_placeholder(self):
        swift = Path("/Users/calderwong/Desktop/hapa-living-comic/swiftui/LivingComicBook/LivingComicBook/main.swift").read_text()
        self.assertIn("import AVKit", swift)
        self.assertIn("AsyncImage", swift)
        self.assertIn("VideoPlayer", swift)
        self.assertIn("assetURL", swift)
        self.assertIn("assets", swift)
        self.assertIn("LTX motion layer", swift)


if __name__ == "__main__":
    unittest.main()
