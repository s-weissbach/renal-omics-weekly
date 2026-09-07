#!/usr/bin/env python3
"""Normalize a NotebookLM download to a podcast-friendly M4A file."""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
from pathlib import Path


def duration(path: Path) -> tuple[str, float]:
    result = subprocess.run(["afinfo", str(path)], check=True, capture_output=True, text=True)
    match = re.search(r"estimated duration:\s*([\d.]+) sec", result.stdout)
    if not match:
        raise RuntimeError("Could not determine audio duration with afinfo")
    seconds = float(match.group(1))
    total = round(seconds)
    return f"{total // 3600:02d}:{(total % 3600) // 60:02d}:{total % 60:02d}", seconds


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    if args.output.exists():
        raise SystemExit(f"Refusing to overwrite {args.output}")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    if args.input.suffix.lower() in {".m4a", ".mp4"}:
        shutil.copy2(args.input, args.output)
    else:
        subprocess.run(
            ["afconvert", str(args.input), str(args.output), "-f", "m4af", "-d", "aac", "-b", "128000"],
            check=True,
        )
    formatted, seconds = duration(args.output)
    print(json.dumps({"path": str(args.output), "bytes": args.output.stat().st_size, "duration": formatted, "seconds": seconds, "mime_type": "audio/mp4"}, indent=2))


if __name__ == "__main__":
    main()

