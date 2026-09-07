#!/usr/bin/env python3
"""Upload an episode as a GitHub Release asset and publish the refreshed feed."""

from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def run(*args: str) -> str:
    result = subprocess.run(args, cwd=ROOT, check=True, capture_output=True, text=True)
    return result.stdout.strip()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("episode_dir", type=Path)
    parser.add_argument("audio", type=Path)
    parser.add_argument("--publish", action="store_true")
    args = parser.parse_args()

    episode_dir = args.episode_dir.resolve()
    episode = json.loads((episode_dir / "episode.json").read_text())
    config = json.loads((ROOT / "podcast.json").read_text())
    audio = args.audio.resolve()
    if not audio.exists():
        raise SystemExit(f"Missing audio: {audio}")
    if not config.get("owner_email"):
        raise SystemExit("Set owner_email in podcast.json before publishing; Spotify uses it for one-time feed verification.")

    tag = episode["release_tag"]
    filename = episode["audio_filename"]
    asset_url = f'https://github.com/{config["repository"]}/releases/download/{tag}/{filename}'
    episode["audio_url"] = asset_url
    episode["length_bytes"] = audio.stat().st_size
    (episode_dir / "episode.json").write_text(json.dumps(episode, indent=2, ensure_ascii=False) + "\n")

    subprocess.run(["python3", str(ROOT / "scripts" / "render_feed.py")], cwd=ROOT, check=True)
    if not args.publish:
        print("Prepared locally. Re-run with --publish to create the release and push the feed.")
        return

    notes = episode_dir / "release_notes.md"
    run("gh", "release", "create", tag, f"{audio}#{filename}", "--repo", config["repository"], "--title", episode["title"], "--notes-file", str(notes))
    run("git", "add", "podcast.json", "state/seen.json", "episodes", "docs")
    status = run("git", "status", "--porcelain")
    if status:
        run("git", "commit", "-m", f'Publish {episode["title"]}')
        run("git", "push", "origin", "main")
    print(asset_url)


if __name__ == "__main__":
    main()

