import tempfile
import unittest
from pathlib import Path

from living_comic.models import ComicIssue, ComicPanel
from living_comic.storage import ProjectStore


class ComicModelTests(unittest.TestCase):
    def test_issue_roundtrip_preserves_panels_and_assets(self):
        issue = ComicIssue(
            id="issue-1",
            title="Thor Tests the Campfire",
            logline="A cat interrupts an AI comic pipeline.",
            style="dark comic ink",
            panels=[
                ComicPanel(
                    id="p1",
                    page=1,
                    panel=1,
                    action="Thor steps on the keyboard.",
                    dialogue=[{"speaker": "Thor", "text": "Mrrp."}],
                    visual_prompt="low angle cat paw on glowing keyboard",
                    camera="slow push in",
                )
            ],
        )
        with tempfile.TemporaryDirectory() as tmp:
            store = ProjectStore(Path(tmp))
            saved = store.save_issue(issue)
            loaded = store.load_issue(saved.name)
        self.assertEqual(loaded.title, issue.title)
        self.assertEqual(loaded.panels[0].dialogue[0]["speaker"], "Thor")


if __name__ == "__main__":
    unittest.main()
