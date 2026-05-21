import tempfile
import unittest
from pathlib import Path

from living_comic.pipeline import ComicPipeline, MockLLM, MockImageGenerator, MockLTXAnimator, MockTTS
from living_comic.storage import ProjectStore


class PipelineTests(unittest.TestCase):
    def test_generate_full_issue_creates_project_assets(self):
        with tempfile.TemporaryDirectory() as tmp:
            store = ProjectStore(Path(tmp))
            pipeline = ComicPipeline(
                store=store,
                llm=MockLLM(),
                image_generator=MockImageGenerator(),
                animator=MockLTXAnimator(),
                tts=MockTTS(),
            )
            issue = pipeline.generate_full_issue("Calder and Thor meet the Huemon Trainer", panel_count=3)
            self.assertEqual(len(issue.panels), 3)
            for panel in issue.panels:
                self.assertTrue((store.assets_dir / panel.image_path).exists())
                self.assertTrue((store.assets_dir / panel.video_path).exists())
                self.assertTrue((store.assets_dir / panel.audio_path).exists())


if __name__ == "__main__":
    unittest.main()
