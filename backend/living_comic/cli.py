from __future__ import annotations

import argparse
import os
from pathlib import Path

from .providers import build_pipeline
from .storage import ProjectStore


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate a local living comic prototype issue.")
    parser.add_argument("idea")
    parser.add_argument("--data", default=os.environ.get("LIVING_COMIC_DATA", "./runtime"))
    parser.add_argument("--panels", type=int, default=6)
    parser.add_argument("--style", default="dark polished comic, Apple Silicon local-first")
    parser.add_argument("--hermes", action="store_true")
    parser.add_argument("--profile", default="default")
    parser.add_argument("--provider", default=None, help="mock or hapa-ltx; defaults to LIVING_COMIC_PROVIDER")
    parser.add_argument("--tts-provider", default=None, help="mock, mac-say, or command; defaults to LIVING_COMIC_TTS_PROVIDER")
    args = parser.parse_args()
    pipeline = build_pipeline(
        ProjectStore(Path(args.data)),
        use_hermes=args.hermes,
        hermes_profile=args.profile,
        provider=args.provider,
        tts_provider=args.tts_provider,
    )
    issue = pipeline.generate_full_issue(args.idea, args.panels, args.style)
    print(f"Generated {issue.id}: {issue.title}")


if __name__ == "__main__":
    main()
