import tempfile
import unittest
from pathlib import Path

from fastapi.testclient import TestClient

from living_comic.api.server import create_app

REPO_ROOT = Path(__file__).resolve().parents[1]


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

    def test_docs_endpoints_expose_readme_from_allowlist(self):
        with tempfile.TemporaryDirectory() as tmp:
            client = TestClient(create_app(Path(tmp)))
            index = client.get("/api/docs")
            self.assertEqual(index.status_code, 200)
            payload = index.json()
            self.assertIn("docs", payload)
            self.assertIn("fixed allowlist", payload["safety"])
            readme_entry = next(doc for doc in payload["docs"] if doc["id"] == "readme")
            self.assertTrue(readme_entry["exists"])
            self.assertEqual(readme_entry["status"], "available")
            self.assertEqual(readme_entry["source"], "README.md")
            self.assertEqual(payload["root"], "hapa-living-comic")

            readme = client.get("/api/docs/readme")
            self.assertEqual(readme.status_code, 200)
            self.assertEqual(readme.json()["title"], "README.md")
            self.assertEqual(readme.json()["source"], "README.md")
            self.assertIn("Hapa Living Comic Book", readme.json()["markdown"])

            blocked = client.get("/api/docs/../../README.md")
            self.assertEqual(blocked.status_code, 404)

    def test_swiftui_renders_media_assets_not_text_only_placeholder(self):
        swift = (REPO_ROOT / "swiftui/LivingComicBook/LivingComicBook/main.swift").read_text()
        self.assertIn("import AVKit", swift)
        self.assertIn("AsyncImage", swift)
        self.assertIn("VideoPlayer", swift)
        self.assertIn("assetURL", swift)
        self.assertIn("assets", swift)
        self.assertIn("LTX motion layer", swift)
        self.assertIn("Docs / README", swift)
        self.assertIn("/api/docs", swift)
        self.assertIn("DOCS UNKNOWN", swift)
        self.assertIn("AttributedString(markdown:", swift)


if __name__ == "__main__":
    unittest.main()
