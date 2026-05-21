from __future__ import annotations

import argparse
from pathlib import Path

from .pipeline import ComicPipeline, HermesLLM, MockImageGenerator, MockLLM, MockLTXAnimator, MockTTS
from .storage import ProjectStore


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate a local living comic prototype issue.")
    parser.add_argument("idea")
    parser.add_argument("--data", default="./runtime")
    parser.add_argument("--panels", type=int, default=6)
    parser.add_argument("--style", default="dark polished comic, Apple Silicon local-first")
    parser.add_argument("--hermes", action="store_true")
    parser.add_argument("--profile", default="default")
    args = parser.parse_args()
    llm = HermesLLM(args.profile) if args.hermes else MockLLM()
    issue = ComicPipeline(ProjectStore(Path(args.data)), llm, MockImageGenerator(), MockLTXAnimator(), MockTTS()).generate_full_issue(args.idea, args.panels, args.style)
    print(f"Generated {issue.id}: {issue.title}")


if __name__ == "__main__":
    main()
